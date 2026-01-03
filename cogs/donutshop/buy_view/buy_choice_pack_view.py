from library.botapp import miru_client, botapp
from library.dbmodules import dbcards
import logging
import hikari
import miru

tier_word = {
    1: "Standard",
    2: "Event",
    3: "Limited"
}

def gen_poscards_str(filter):
    all_pos_cards = dbcards.filtered_get_card(
        filter_string=filter,
        fetch_one=False
    )

    text_list = []
    for card in all_pos_cards:
        text_list.append(f"({card['identifier']}) {tier_word[card['tier']]} card - {card['name']} {botapp.d['rarity_emojis_text'][card['rarity']]}")

    return text_list

class main_view:
    def __init__(self, item_id):
        from library.dbmodules.donutshop import get_item
        self.item_id = item_id
        self.pack = get_item(item_id=item_id)

    def gen_embed(self):
        pack_list = gen_poscards_str(self.pack['filter'])

        embed = (
            hikari.Embed(
                title="Your selected pack!",
                description=f"You've picked a pack worth {self.pack['price']} {botapp.d['coin_name']['normal']} with {self.pack['amount']} cards inside!"
            )
            .add_field(
                name="Possible cards",
                value=f"You can possibly get the following cards from this pack: +"
                "\n".join([f"- {card}" for card in pack_list])
            )
        )
        return embed

    def init_view(self):
        card_pack = self.pack
        gen_embed = self.gen_embed
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
            @miru.button(label="Buy Choice Pack!")
            async def abtn(self, ctx: miru.ViewContext, select: miru.Button) -> None:
                class MyModal(miru.Modal, title=f"Choose {card_pack['amount']} Cards!"):
                    card_ids = miru.TextInput(
                        label="Choice Card",
                        placeholder="Enter a list of card IDs separated by commas",
                        required=True,
                        max_length=1000,
                        style=hikari.TextInputStyle.SHORT,
                    )

                    # The callback function is called after the user hits 'Submit'
                    async def callback(self, ctx: miru.ModalContext) -> None:
                        cardids_value = self.card_ids.value
                        if cardids_value.endswith(","):
                            cardids_value = cardids_value[0:len(cardids_value) - 1]  # Remove trailing comma
                        card_choices = [str(choice).strip() for choice in str(cardids_value).split(",")]

                        all_pos_cards = dbcards.filtered_get_card(
                            filter_string=card_pack['filter'],
                            fetch_one=False
                        )
                        all_pos_cards = [str(card['identifier']) for card in all_pos_cards]

                        if len(card_choices) > card_pack['amount']:
                            embed = gen_embed()
                            embed.add_field(
                                name="Too many!",
                                value=f"You asked for {len(card_choices) - card_pack['amount']} too many cards. This pack is for {card_pack['amount']} cards."
                            )
                            await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)
                            return
                        elif len(card_choices) < card_pack["amount"]:
                            embed = gen_embed()
                            embed.add_field(
                                name="Too few!",
                                value=f"You asked for {card_pack['amount'] - len(card_choices)} too few cards. This pack is for {card_pack['amount']} cards."
                            )
                            await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)
                            return

                        for choice in card_choices:
                            if choice not in all_pos_cards:
                                embed = gen_embed()
                                embed.add_field(
                                    name="Impossible card",
                                    value="You asked for a card that we can't add."
                                )
                                await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)
                                return
                            
                            success = dbcards.spawn_card(card_id=choice, amount=1, user_id=int(ctx.author.id), allow_limited=True)
                            if not success:
                                logging.warning(f"Failed to give {ctx.author.id} card {choice} while they were opening a choice pack.")
                                embed = gen_embed()
                                embed.add_field(
                                    name="ERROR",
                                    value="Failed to add a card to your inventory! Please file a bug report."
                                )
                                ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)
                                return
                            
                        # No errors
                        embed = gen_embed()
                        embed.add_field(
                            name="Pack Purchased!",
                            value=f"You purchased the pack, and got {card_pack['amount']} cards of your choice!\nYou chose: *{", ".join(card_choices)}*"
                        )
                        await ctx.respond(embed)
                        return

                modal = MyModal()
                builder = modal.build_response(miru_client)
                await builder.create_modal_response(ctx.interaction)
                miru_client.start_modal(modal)

        menu = Menu_Init()

        return menu