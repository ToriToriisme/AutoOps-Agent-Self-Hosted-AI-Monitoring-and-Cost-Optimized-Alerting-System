import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

DB_PATH = "storage/agent.db"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db_connection()
    cursor = conn.cursor()

    # Bảng 1: agent_tasks
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

    # Bảng 2: audit_logs
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
    
    # Đảm bảo severity là string
    severity_str = (
        json.dumps(severity, ensure_ascii=False)
        if isinstance(severity, (list, dict))
        else str(severity)
    )

    cursor.execute(
        """
        INSERT INTO agent_tasks (task_id, alert_title, labels_json, severity, proposed_action, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (task_id, alert_title, labels_json, severity_str, action_str, status, now_str, now_str),
    )
    conn.commit()
    conn.close()


def update_agent_task_status(task_id: str, status: str) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now(timezone.utc).isoformat()

    cursor.execute(
        """
        UPDATE agent_tasks
        SET status = ?, updated_at = ?
        WHERE task_id = ?
    """,
        (status, now_str, task_id),
    )
    conn.commit()
    conn.close()

def get_agent_task(task_id: str) -> dict | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agent_tasks WHERE task_id = ?", (task_id,))
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
    
    # Đảm bảo decision_reason là string (phòng trường hợp AI trả về list)
    reason_str = (
        json.dumps(decision_reason, ensure_ascii=False)
        if isinstance(decision_reason, (list, dict))
        else str(decision_reason)
    )
    
    # Đảm bảo execution_output là string
    output_str = (
        json.dumps(execution_output, ensure_ascii=False)
        if isinstance(execution_output, (list, dict))
        else str(execution_output)
    )

    cursor.execute(
        """
        INSERT INTO audit_logs (
            task_id, rag_context_used, rag_context_refs, decision_reason,
            execution_result, execution_output, processing_time_ms,
            prompt_tokens, completion_tokens
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
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
