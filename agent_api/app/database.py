import os
import json
import sqlite3
from datetime import datetime, timezone
from typing import Any
from pathlib import Path
from dotenv import load_dotenv

# Tự động tìm đường dẫn tuyệt đối đến file .env
base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

# Các cấu hình kết nối database
DATABASE_URL = os.getenv("DATABASE_URL")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Kiểm tra xem có cấu hình PostgreSQL không
IS_POSTGRES = bool(DATABASE_URL or DB_HOST)

DB_PATH = "storage/agent.db"


def get_db_connection() -> Any:
    if IS_POSTGRES:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        if DATABASE_URL:
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        else:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                cursor_factory=RealDictCursor
            )
        return conn
    else:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn


def init_db() -> None:
    conn = get_db_connection()
    cursor = conn.cursor()

    if IS_POSTGRES:
        # Bảng 1: agent_tasks cho PostgreSQL
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_tasks (
                task_id TEXT PRIMARY KEY,
                alert_title TEXT,
                labels_json TEXT,
                severity TEXT,
                proposed_action TEXT,
                status TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Bảng 2: audit_logs cho PostgreSQL (sử dụng SERIAL thay vì AUTOINCREMENT)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id SERIAL PRIMARY KEY,
                task_id TEXT,
                rag_context_used TEXT,
                rag_context_refs TEXT,
                decision_reason TEXT,
                execution_result TEXT,
                execution_output TEXT,
                processing_time_ms INTEGER,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                FOREIGN KEY(task_id) REFERENCES agent_tasks(task_id)
            )
        """)
    else:
        # Bảng 1: agent_tasks cho SQLite
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_tasks (
                task_id TEXT PRIMARY KEY,
                alert_title TEXT,
                labels_json TEXT,
                severity TEXT,
                proposed_action TEXT,
                status TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Bảng 2: audit_logs cho SQLite
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                rag_context_used TEXT,
                rag_context_refs TEXT,
                decision_reason TEXT,
                execution_result TEXT,
                execution_output TEXT,
                processing_time_ms INTEGER,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                FOREIGN KEY(task_id) REFERENCES agent_tasks(task_id)
            )
        """)

    conn.commit()
    conn.close()


def insert_agent_task(
    task_id: str,
    alert_title: str,
    labels: dict[str, Any],
    severity: str,
    proposed_action: str | dict[str, Any],
    status: str,
) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now(timezone.utc).isoformat()

    labels_json = json.dumps(labels, ensure_ascii=False)
    action_str = (
        json.dumps(proposed_action, ensure_ascii=False)
        if isinstance(proposed_action, (dict, list))
        else str(proposed_action)
    )
    
    severity_str = (
        json.dumps(severity, ensure_ascii=False)
        if isinstance(severity, (list, dict))
        else str(severity)
    )

    query = """
        INSERT INTO agent_tasks (task_id, alert_title, labels_json, severity, proposed_action, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    if IS_POSTGRES:
        query = query.replace("?", "%s")

    cursor.execute(
        query,
        (task_id, alert_title, labels_json, severity_str, action_str, status, now_str, now_str),
    )
    conn.commit()
    conn.close()


def update_agent_task_status(task_id: str, status: str) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now(timezone.utc).isoformat()

    query = """
        UPDATE agent_tasks
        SET status = ?, updated_at = ?
        WHERE task_id = ?
    """
    if IS_POSTGRES:
        query = query.replace("?", "%s")

    cursor.execute(
        query,
        (status, now_str, task_id),
    )
    conn.commit()
    conn.close()


def get_agent_task(task_id: str) -> dict | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM agent_tasks WHERE task_id = ?"
    if IS_POSTGRES:
        query = query.replace("?", "%s")

    cursor.execute(query, (task_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def insert_audit_log(
    task_id: str,
    rag_context_used: str | list | dict,
    rag_context_refs: list[str],
    decision_reason: str,
    execution_result: str,
    execution_output: str,
    processing_time_ms: int,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()

    context_str = (
        json.dumps(rag_context_used, ensure_ascii=False)
        if isinstance(rag_context_used, (list, dict))
        else str(rag_context_used)
    )
    refs_str = json.dumps(rag_context_refs, ensure_ascii=False)
    
    reason_str = (
        json.dumps(decision_reason, ensure_ascii=False)
        if isinstance(decision_reason, (list, dict))
        else str(decision_reason)
    )
    
    output_str = (
        json.dumps(execution_output, ensure_ascii=False)
        if isinstance(execution_output, (list, dict))
        else str(execution_output)
    )

    query = """
        INSERT INTO audit_logs (
            task_id, rag_context_used, rag_context_refs, decision_reason,
            execution_result, execution_output, processing_time_ms,
            prompt_tokens, completion_tokens
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    if IS_POSTGRES:
        query = query.replace("?", "%s")

    cursor.execute(
        query,
        (
            task_id,
            context_str,
            refs_str,
            reason_str,
            execution_result,
            output_str,
            processing_time_ms,
            prompt_tokens,
            completion_tokens,
        ),
    )
    conn.commit()
    conn.close()

