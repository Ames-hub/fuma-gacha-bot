from library.database import pokemarket, economy
from library.botapp import botapp
import datetime
import hikari
import miru

rarity_crossref = {
    1: "<:loveball:1389313177392513034>",
    2: "<:loveball:1389313177392513034>" * 2,
    3: "<:loveball:1389313177392513034>" * 3,
    4: "<:loveball:1389313177392513034>" * 4,
    5: "<:loveball:1389313177392513034>" * 5,
}

item_type_crossref = {
    0: "Random",
    1: "Choice",
}

class main_view:
    @staticmethod
    def gen_embed(member_id):
        member_id = int(member_id)
        cache = dict(botapp.d['pokestore']['user_cache']).get(str(member_id))
        if not cache:
            botapp.d['pokestore']['user_cache'][str(member_id)] = 0
            viewing_page = 0
        else:
            viewing_page = cache

        embed = (
            hikari.Embed(
                title="PokeMarket",
                description="View below the great card packs available for purchase!",
            )
        )

        all_items = pokemarket.get_all_items()
        if len(all_items) == 0:
            embed.add_field(
                name="Card Packs",
                value="No cards found!"
            )
            embed.set_footer("No offers available")
            return embed

        if viewing_page != 0:
            try:
                item = all_items[viewing_page - 1]
            except IndexError:
                item = "No items found!"

            # noinspection PyTypeChecker
            embed.add_field(
                name="Card Packs",
                value=f"✨ *{item['item_id']}*\n{item['amount']} Cards are in this pack\n"
                      f"{item_type_crossref[item['type']]} Pack for **{item['price']} PokeCoins** ✨"
            )
            embed.set_footer(f"Page {viewing_page}/{len(all_items)}")
        else:
            shop_str = ""
            for item in all_items:
                shop_str += f"✨ *{item['item_id']}* - {item['amount']} Cards, {item_type_crossref[item['type']]} Pack for **{item['price']} PokeCoins** ✨\n\n"

            embed.add_field(
                name="Card Packs",
                value=shop_str
            )
            embed.set_footer(
                "All Offers available"
            )

        return embed

    @staticmethod
    def init_view():
        # noinspection PyUnusedLocal
        class Menu_Init(miru.View):
            @miru.button(label="Buy", emoji="💰", style=hikari.ButtonStyle.SUCCESS, custom_id="purchase", disabled=True)  # Disabled for page 1
            async def buy_btn(self, ctx: miru.ViewContext, button: miru.Button) -> None:
                embed = main_view.gen_embed(ctx.author.id)

                # Get the pack, find what cards they got.
                item_id = botapp.d['pokestore']['user_cache'][str(ctx.author.id)]
                pack = pokemarket.get_all_items()[item_id - 1]

                account = economy.account(ctx.author.id)
                if account.fumacoins.balance() >= pack['price']:
                    money_success = account.fumacoins.modify_balance(pack['price'], "subtract")
                    if money_success is False:
                        embed.add_field(
                            name="Couldn't buy it!",
                            value="Something went wrong when attempting to take payment.",
                        )
                    else:
                        item_give_success = pokemarket.give_random_pack(ctx.author.id, pack['item_id'])
                        if item_give_success is True:
                            embed.add_field(
                                name="Item Purchased!",
                                value=f"You bought a new card pack <t:{int(datetime.datetime.now().timestamp())}:R>!\n",
                            )
                        elif item_give_success == -1:
                            embed.add_field(
                                name="Couldn't buy it!",
                                value="No items that fit the criteria that this pack can get you can be found!\n"
                                      "(There's no qualified cards.)",
                            )
                        else:
                            # TODO: Make this remove any cards it DID give you if it failed.
                            money_success = account.fumacoins.modify_balance(pack['price'], "add")
                            embed.add_field(
                                name="Couldn't buy it!",
                                value="Something went wrong when attempting to give you the item. You've been refunded.",
                            )
                else:
                    embed.add_field(
                        name="Couldn't buy it!",
                        value=f"You don't have enough coins to buy this item!\n",
                    )

                await ctx.edit_response(embed=embed)

            @miru.button(label="Back", emoji="◀️", style=hikari.ButtonStyle.SECONDARY, custom_id="backbtn", disabled=True)  # Disabled for page 1
            async def back_btn(self, ctx: miru.ViewContext, button: miru.Button) -> None:
                botapp.d['pokestore']['user_cache'][str(ctx.author.id)] -= 1
                embed = main_view.gen_embed(ctx.author.id)

                if botapp.d['pokestore']['user_cache'][str(ctx.author.id)] == 0:
                    # Disable self
                    self.children[1].disabled = True
                    # Disable purchasing
                    self.children[0].disabled = True

                await ctx.edit_response(embed=embed, components=self)

            @miru.button(label="Next", emoji="▶️", style=hikari.ButtonStyle.SECONDARY)
            async def Next_btn(self, ctx: miru.ViewContext, button: miru.Button) -> None:
                botapp.d['pokestore']['user_cache'][str(ctx.author.id)] += 1
                embed = main_view.gen_embed(ctx.author.id)

                if botapp.d['pokestore']['user_cache'][str(ctx.author.id)] == 1:
                    # Enable the ability to go back
                    self.children[1].disabled = False
                    # Enable purchasing
                    self.children[0].disabled = False

                await ctx.edit_response(embed=embed, components=self)

            # noinspection PyUnusedLocal
            @miru.button(label="Stop Browsing", style=hikari.ButtonStyle.DANGER)
            async def stop_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
                botapp.d['pokestore']['user_cache'][str(ctx.author.id)] = 0
                await ctx.edit_response(
                    embed=main_view.gen_embed(ctx.author.id),
                    components=[],
                )
                self.stop()  # Called to stop the view

        menu = Menu_Init()

        return menu