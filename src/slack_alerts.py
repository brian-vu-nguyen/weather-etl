"""
Slack notification callbacks built on
`airflow.providers.slack.notifications.slack.send_slack_notification`.

Prerequisites
-------------
• A “Slack API” connection (Conn ID **slack_api**) that holds an *xoxb-…*
  bot token with `chat:write` scope.  
• The bot is already a member of the channel you’ll post to.
"""

from __future__ import annotations

from urllib.parse import quote_plus
from airflow.configuration import conf
from airflow.providers.slack.notifications.slack import send_slack_notification

# one place to change IDs / channel
_SLACK_CONN   = "slack_api"
_SLACK_CHAN   = "pipelines"          # or "#pipelines" or channel-ID

# ---- notifier objects -----------------------------------------------------
notify_task_failure = send_slack_notification(
    slack_conn_id=_SLACK_CONN,
    channel=_SLACK_CHAN,
    text=(
        ":red_circle: Task *{{ ti.task_id }}* in DAG *{{ dag.dag_id }}* "
        "failed (run {{ run_id }})."
    ),
)