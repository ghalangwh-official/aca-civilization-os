"""ACA Cloud Kernel ingestion gateway.

This service consumes robot telemetry from Kafka and persists normalized
measurements into TimescaleDB.

The module keeps configuration in environment variables, avoids hardcoded
secrets, and can still be imported in environments where Kafka or PostgreSQL
drivers are not installed yet (for example during unit tests).
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any

try:  # pragma: no cover - exercised in runtime environment
    import psycopg2
    from psycopg2 import OperationalError
except ImportError:  # pragma: no cover - import guard for test environments
    psycopg2 = None

    class OperationalError(Exception):
        """Fallback when psycopg2 is unavailable."""


try:  # pragma: no cover - exercised in runtime environment
    from kafka import KafkaConsumer
    from kafka.errors import KafkaError, NoBrokersAvailable
except ImportError:  # pragma: no cover - import guard for test environments
    KafkaConsumer = None

    class KafkaError(Exception):
        """Fallback when kafka-python is unavailable."""

    class NoBrokersAvailable(KafkaError):
        """Fallback when kafka-python is unavailable."""

log = logging.getLogger("aca.gateway")

DEFAULT_DB_HOST = "localhost"
DEFAULT_DB_PORT = 5432
DEFAULT_DB_NAME = "aca_civilization_ledger"
DEFAULT_DB_USER = "aca_architect"
DEFAULT_KAFKA_BROKER = "localhost:9092"
DEFAULT_KAFKA_TOPIC = "aca.builder.telemetry"
DEFAULT_KAFKA_GROUP_ID = "aca-kernel-core-gateway"


@dataclass(frozen=True)
class Settings:
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    kafka_broker: str
    kafka_topic: str
    kafka_group_id: str
    poll_timeout_ms: int

    @classmethod
    def from_env(cls) -> "Settings":
        db_password = os.getenv("ACA_DB_PASSWORD", "")
        if not db_password:
            raise RuntimeError(
                "ACA_DB_PASSWORD is required. Set it in the environment or in aca-kernel-core/.env."
            )
        return cls(
            db_host=os.getenv("ACA_DB_HOST", DEFAULT_DB_HOST),
            db_port=int(os.getenv("ACA_DB_PORT", str(DEFAULT_DB_PORT))),
            db_name=os.getenv("ACA_DB_NAME", DEFAULT_DB_NAME),
            db_user=os.getenv("ACA_DB_USER", DEFAULT_DB_USER),
            db_password=db_password,
            kafka_broker=os.getenv("ACA_KAFKA_BROKER", DEFAULT_KAFKA_BROKER),
            kafka_topic=os.getenv("ACA_KAFKA_TOPIC", DEFAULT_KAFKA_TOPIC),
            kafka_group_id=os.getenv("ACA_KAFKA_GROUP_ID", DEFAULT_KAFKA_GROUP_ID),
            poll_timeout_ms=int(os.getenv("ACA_KAFKA_POLL_TIMEOUT_MS", "1000")),
        )


def setup_logging() -> None:
    logging.basicConfig(
        level=os.getenv("ACA_LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def get_db_connection(settings: Settings):
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is not installed in this environment.")
    return psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )


def init_db(settings: Settings) -> None:
    """Create extension, table, and hypertable if possible."""
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is not installed in this environment.")
    with get_db_connection(settings) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS raw_robot_telemetry (
                    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    robot_id VARCHAR(50) NOT NULL,
                    battery_voltage DOUBLE PRECISION NOT NULL,
                    velocity_rps DOUBLE PRECISION NOT NULL
                );
                """
            )
            try:
                cur.execute(
                    """
                    SELECT create_hypertable(
                        'raw_robot_telemetry',
                        'time',
                        if_not_exists => TRUE
                    );
                    """
                )
            except psycopg2.Error as exc:
                # The table is still usable even if hypertable conversion fails.
                log.warning("Timescale hypertable setup skipped: %s", exc)


def parse_payload(raw_message: Any) -> dict[str, Any]:
    if isinstance(raw_message, bytes):
        raw_message = raw_message.decode("utf-8")
    if isinstance(raw_message, str):
        return json.loads(raw_message)
    if isinstance(raw_message, dict):
        return raw_message
    raise TypeError(f"Unsupported Kafka payload type: {type(raw_message)!r}")


def extract_measurements(payload: dict[str, Any]) -> tuple[str, float, float]:
    robot_id = payload["robot_id"]
    battery_voltage = payload["battery_voltage"]
    velocity_rps = payload["kinematics"]["current_velocity_rps"]
    return str(robot_id), float(battery_voltage), float(velocity_rps)


def insert_row(settings: Settings, robot_id: str, battery_voltage: float, velocity_rps: float) -> None:
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is not installed in this environment.")
    with get_db_connection(settings) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO raw_robot_telemetry (robot_id, battery_voltage, velocity_rps)
                VALUES (%s, %s, %s);
                """,
                (robot_id, battery_voltage, velocity_rps),
            )
        conn.commit()


def wait_for_database(settings: Settings, retries: int = 30, delay_seconds: float = 2.0) -> None:
    for attempt in range(1, retries + 1):
        try:
            init_db(settings)
            log.info("Database ready.")
            return
        except OperationalError as exc:
            log.warning("Database not ready yet (%s/%s): %s", attempt, retries, exc)
            time.sleep(delay_seconds)
    raise RuntimeError("TimescaleDB is not ready after retrying.")


def create_consumer(settings: Settings) -> KafkaConsumer:
    if KafkaConsumer is None:
        raise RuntimeError("kafka-python is not installed in this environment.")
    return KafkaConsumer(
        settings.kafka_topic,
        bootstrap_servers=[settings.kafka_broker],
        group_id=settings.kafka_group_id,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda value: value,
    )


def run(settings: Settings) -> None:
    wait_for_database(settings)

    while True:
        try:
            consumer = create_consumer(settings)
            break
        except NoBrokersAvailable as exc:
            log.warning("Kafka broker not ready yet: %s", exc)
            time.sleep(2)

    log.info(
        "Gateway started. Kafka topic=%s broker=%s db=%s:%s/%s",
        settings.kafka_topic,
        settings.kafka_broker,
        settings.db_host,
        settings.db_port,
        settings.db_name,
    )

    try:
        while True:
            batches = consumer.poll(timeout_ms=settings.poll_timeout_ms)
            if not batches:
                continue

            for _, records in batches.items():
                for record in records:
                    try:
                        payload = parse_payload(record.value)
                        robot_id, battery_voltage, velocity_rps = extract_measurements(payload)
                        insert_row(settings, robot_id, battery_voltage, velocity_rps)
                        consumer.commit()
                        log.info(
                            "Telemetry ingested robot_id=%s battery_voltage=%.3f velocity_rps=%.3f",
                            robot_id,
                            battery_voltage,
                            velocity_rps,
                        )
                    except KeyError as exc:
                        log.error("Telemetry contract violation: missing key %s", exc, exc_info=True)
                    except json.JSONDecodeError as exc:
                        log.error("Invalid telemetry JSON: %s", exc, exc_info=True)
                    except (TypeError, ValueError) as exc:
                        log.error("Telemetry parsing failed: %s", exc, exc_info=True)
                    except psycopg2.Error as exc:
                        log.error("Database insert failed: %s", exc, exc_info=True)
                    except KafkaError as exc:
                        log.error("Kafka error while processing telemetry: %s", exc, exc_info=True)
    except KeyboardInterrupt:
        log.info("Gateway stopped by user.")
    finally:
        consumer.close()


def main() -> None:
    setup_logging()
    settings = Settings.from_env()
    run(settings)


if __name__ == "__main__":
    main()
