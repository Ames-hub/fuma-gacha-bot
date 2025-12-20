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
                title="Feedback",
                description="Suggestions, Ideas, complaints! Let us know!\nClick the button below to begin."
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
            @miru.button(label="Show Feedback Screen!")
            async def button(self, ctx: miru.ViewContext, select: miru.Button) -> None:
                class MyModal(miru.Modal, title="Bug Report Screen"):
                    feedback = miru.TextInput(
                        label="feedback",
                        placeholder="What's your feedback?",
                        required=True,
                        max_length=1500,
                        style=hikari.TextInputStyle.PARAGRAPH,
                    )

                    # The callback function is called after the user hits 'Submit'
                    async def callback(self, ctx: miru.ModalContext) -> None:
                        dmc = await botapp.rest.create_dm_channel(botapp.d['maintainer'])
                        await dmc.send(
                            hikari.Embed(
                                title="Feedback Report",
                                description=f"We've heard some feedback from {ctx.author.username}! ({ctx.author.id})"
                            )
                            .add_field(
                                name="They said...",
                                value=self.feedback.value
                            )
                        )
                        await ctx.respond(
                            hikari.Embed(
                                title="Feedback sent!",
                                description="Thank you for the feedback!"
                            )
                        )

                modal = MyModal()
                builder = modal.build_response(miru_client)
                await builder.create_modal_response(ctx.interaction)
                miru_client.start_modal(modal)

        menu = Menu_Init()

        return menu