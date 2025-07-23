from library.database import eventlogs, events, dbcards
from library.botapp import tasks, botapp
import lightbulb
import datetime

plugin = lightbulb.Plugin(__name__)

@tasks.task(s=10, wait_before_execution=False, auto_start=True)
async def event_notifications():
    if 'event_checked_cache' not in botapp.d:
        botapp.d['event_checked_cache'] = {}

    events_list = events.get_all_events()
    for event_name in events_list:
        schedules = events.get_event_schedule(event_name)
        if schedules is None:
            continue

        for schedule in schedules:
            start_time: datetime.datetime = datetime.datetime.strptime(
                schedule['start_time'],
                "%Y-%m-%d %H:%M:%S"
            )
            end_time: datetime.datetime = datetime.datetime.strptime(
                schedule['end_time'],
                "%Y-%m-%d %H:%M:%S"
            )

            now = datetime.datetime.now()
            later_than_start = now.timestamp() >= start_time.timestamp()
            later_than_end = now.timestamp() >= end_time.timestamp()

            if later_than_start and not later_than_end:
                if botapp.d['event_checked_cache'].get(event_name, False):
                    continue

                # Get all associated cards and mark them as pullable
                cards_list = events.get_assosciated_cards(event_name)
                for card in cards_list:
                    success = dbcards.set_pullability(
                        card_id=card,
                        value=True
                    )
                    if not success:
                        await eventlogs.log_event(
                            "Event Error Warning",
                            f"I failed to mark the card with the ID \"{card}\" as pullable for event \"{event_name}\"."
                        )

                await eventlogs.log_event(
                    "Event Notification",
                    f"The event \"{event_name}\" has started at {start_time}!"
                )

                # Mark as checked only after a successful start
                botapp.d['event_checked_cache'][event_name] = True

            elif later_than_end:
                # Get all associated cards and mark them as not pullable
                cards_list = events.get_assosciated_cards(event_name)
                for card in cards_list:
                    success = dbcards.set_pullability(
                        card_id=card,
                        value=False
                    )
                    if not success:
                        await eventlogs.log_event(
                            "Event Error Warning",
                            f"I failed to mark the card with the ID \"{card}\" as not pullable for event \"{event_name}\"."
                        )

                entry_id = schedule['entry_id']
                success = events.delete_schedule(entry_id)
                if not success:
                    await eventlogs.log_event(
                        "Event Error Warning",
                        f"I failed to delete the scheduled event with the ID \"{entry_id}\" after it was completed."
                    )

                await eventlogs.log_event(
                    "Event Notification",
                    f"The event \"{event_name}\" has ended at {end_time}."
                )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)
