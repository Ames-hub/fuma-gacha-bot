from library.dbmodules.bugsdb import create_bug_report_ticket
from library.dbmodules.shared import classify_severity
from library.botapp import miru_client, botapp
import hikari
import miru

class main_view:
    def __init__(self, author_id):
        self.author_id = author_id

    # noinspection PyMethodMayBeStatic
    def gen_embed(self):
        return (
            hikari.Embed(
                title="Bug report",
                description="Thank you for reporting a bug!\n"
            )
            .add_field(
                name="How to report a bug",
                value="1. You need to Click the button below to open the reporting screen.\n\n"
                      "2. When you see the screen, fill out the fields to the best of your ability. Please be specific and detailed ^^\n\n"
                      "3. Once you're done, click the submit button!"
            )
        )

    def init_view(self):
        class Menu_Init(miru.View):
            # noinspection PyUnusedLocal
            @miru.button(label="Cancel", style=hikari.ButtonStyle.DANGER)
            async def stop_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
                await ctx.edit_response(
                    hikari.Embed(
                        title="Exitting menu.",
                        description="Have any suggestions? Be sure to let us know on the github!",
                    ),
                    components=[]
                )
                self.stop()  # Called to stop the view

            # noinspection PyUnusedLocal
            @miru.button(label="Show Reporting Screen!", emoji="🪲")
            async def report_btn(self, ctx: miru.ViewContext, select: miru.Button) -> None:
                class MyModal(miru.Modal, title="Bug Report Screen"):
                    bug = miru.TextInput(
                        label="Bug",
                        placeholder="How would you describe the bug?",
                        required=True,
                        max_length=1000,
                        style=hikari.TextInputStyle.PARAGRAPH,
                    )

                    problem_zone = miru.TextInput(
                        label="Problem Section",
                        placeholder="Where did you find the bug? The pull command?",
                        required=True,
                        max_length=1000,
                        style=hikari.TextInputStyle.SHORT,
                    )

                    expected = miru.TextInput(
                        label="Expected result",
                        placeholder="What did you expect to happen?",
                        required=True,
                        max_length=1000,
                        style=hikari.TextInputStyle.PARAGRAPH,
                    )

                    reproduce = miru.TextInput(
                        label="How do I reproduce it?",
                        placeholder="Write exactly what you did which made the bug happen please!",
                        required=True,
                        max_length=1000,
                        style=hikari.TextInputStyle.PARAGRAPH
                    )

                    additional = miru.TextInput(
                        label="Additional Info",
                        placeholder="Any additional info you'd like to add?",
                        required=False,
                        max_length=1000,
                        style=hikari.TextInputStyle.PARAGRAPH,
                    )

                    # The callback function is called after the user hits 'Submit'
                    async def callback(self, ctx: miru.ModalContext) -> None:
                        additional = self.additional.value
                        if additional == "":
                            additional = None

                        est_severity = classify_severity(self.bug.value)

                        # Remembers that THIS user reported a bug so we can tell them how it went
                        ticket_id = create_bug_report_ticket(
                            reporter_id=ctx.author.id,
                            stated_bug=self.bug.value,
                            reproduction_steps=self.reproduce.value,
                            problem_section=self.problem_zone.value,
                            extra_info=additional,
                            return_ticket=True,
                            expected_result=self.expected.value,
                            severity=est_severity
                        )

                        dmc = await botapp.rest.create_dm_channel(botapp.d['maintainer'])
                        await dmc.send(
                            hikari.Embed(
                                title="Bug Report",
                                description=f"Ticket ID: {ticket_id}\n"
                                            f"Author: {ctx.author.id} ({ctx.author.username})\n"
                                            f"Bug: {self.bug.value}\n"
                                            f"Problem Section: {self.problem_zone.value}\n"
                                            f"Expected Result: {self.expected.value}\n"
                                            f"Reproduction Steps: {self.reproduce.value}\n"
                                            f"Additional Info: {additional}\n"
                                            f"Severity: {est_severity}"
                            )
                        )

                        if ticket_id is not False:
                            await ctx.edit_response(
                                hikari.Embed(
                                    title="Bug reported!",
                                    description="Thank you for reporting the bug!\n"
                                                "The bug has been forwarded to the project maintainers and will be fixed as soon as possible.\n"
                                                f"Your ticket ID: {ticket_id}",
                                    color=0x00ff00,
                                ),
                                components=[]
                            )
                        else:
                            await ctx.edit_response(
                                hikari.Embed(
                                    title="Oh no!",
                                    description="Something went wrong while reporting the bug!\n"
                                                "We've alerted the maintainer to this problem, and we'll fix it as soon as possible.",
                                    color=0xff0000,
                                ),
                            )

                modal = MyModal()
                builder = modal.build_response(miru_client)
                await builder.create_modal_response(ctx.interaction)
                miru_client.start_modal(modal)

        menu = Menu_Init()

        return menu