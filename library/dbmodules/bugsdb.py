from library.botapp import botapp
import traceback
import sqlite3
import logging

DB_PATH = botapp.d['DB_PATH']

def list_bug_reports():
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT bugid, stated_bug, reproduction_steps, problem_section, expected_result, extra_info, reporter_id, report_date, resolved, resolved_at, severity
                FROM bug_reports
                ORDER BY report_date DESC
                """
            )
            rows = cur.fetchall()

            parsed_data = []
            for row in rows:
                parsed_data.append({
                    "bugid": row[0],
                    "stated_bug": row[1],
                    "reproduction_steps": row[2],
                    "problem_section": row[3],
                    "expected_result": row[4],
                    "extra_info": row[5],
                    "reporter_id": row[6],
                    "report_date": row[7],
                    "resolved": row[8],
                    "resolved_at": row[9],
                    "severity": row[10],
                })
            return parsed_data
        except Exception as e:
            logging.error(f"Error while fetching bug reports: {e}", exc_info=e)
            return False

def get_bug_report(bugid):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT bugid, stated_bug, reproduction_steps, problem_section, expected_result, extra_info, reporter_id, report_date, resolved, resolved_at, severity
                FROM bug_reports
                WHERE bugid = ?
                """,
                (bugid,)
            )
            row = cur.fetchone()
            if row:
                return {
                    "bugid": row[0],
                    "stated_bug": row[1],
                    "reproduction_steps": row[2],
                    "problem_section": row[3],
                    "expected_result": row[4],
                    "extra_info": row[5],
                    "reporter_id": row[6],
                    "report_date": row[7],
                    "resolved": row[8],
                    "resolved_at": row[9],
                    "severity": row[10],
                }
            else:
                return None
        except Exception as e:
            logging.error(f"Error while fetching bug report {bugid}: {e}", exc_info=e)
            return None

def mark_bug_report_resolved(bugid):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE bug_reports SET resolved = true, resolved_at = CURRENT_TIMESTAMP WHERE bugid = ?",
                (bugid,)
            )
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error while marking bug report {bugid} as resolved: {e}", exc_info=e)
            return False

def mark_bug_report_unresolved(bugid):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE bug_reports SET resolved = false, resolved_at = NULL WHERE bugid = ?",
                (bugid,)
            )
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error while marking bug report {bugid} as unresolved: {e}", exc_info=e)
            return False

def create_bug_report_ticket(stated_bug, reproduction_steps, problem_section, expected_result, extra_info, reporter_id, severity, return_ticket=False):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO bug_reports (stated_bug, reproduction_steps, problem_section, expected_result, extra_info, reporter_id, severity, report_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (stated_bug, reproduction_steps, problem_section, expected_result, extra_info, reporter_id, severity)
            )
            conn.commit()
            if return_ticket:
                return cur.lastrowid
            return True
        except Exception as e:
            logging.error(f"Error while creating bug report ticket: {e}", exc_info=e)
            return False

def save_traceback(bug_id, exception):
    # unwrap Lightbulb cmd invocation error thing
    actual_exc = exception
    while hasattr(actual_exc, "__cause__") and actual_exc.__cause__:
        actual_exc = actual_exc.__cause__

    exc_type = type(actual_exc).__name__
    exc_traceback = traceback.format_exception(
        type(actual_exc), actual_exc, actual_exc.__traceback__
    )
    exc_traceback_str = "".join(exc_traceback)

    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO bug_tracebacks (bugid, traceback, exc_type)
                VALUES (?, ?, ?)
                """,
                (bug_id, exc_traceback_str, exc_type)
            )
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error while saving traceback: {e}", exc_info=e)
            return False

def get_traceback(bug_id):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT traceback, exc_type FROM bug_tracebacks WHERE bugid = ?
                """,
                (bug_id,)
            )
            row = cur.fetchone()
            if row:
                return {
                    "traceback": str(row[0]).splitlines(),
                    "exc_type": str(row[1]),
                }
            else:
                return None
        except Exception as e:
            logging.error(f"Error while getting bug traceback: {e}", exc_info=e)
            return False