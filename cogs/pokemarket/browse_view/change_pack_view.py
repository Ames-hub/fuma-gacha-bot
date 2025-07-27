from library.database import dbcards, combine_image
from library.botapp import botapp
import hikari
import miru

rarity_crossref = {
    1: "<:loveball:1389313177392513034>",
    2: "<:loveball:1389313177392513034>" * 2,
    3: "<:loveball:1389313177392513034>" * 3,
    4: "<:loveball:1389313177392513034>" * 4,
    5: "<:loveball:1389313177392513034>" * 5,
}

class main_view:
    @staticmethod
    def gen_embed(user_id: int):
        embed = (
            hikari.Embed(
                title="PokeMarket",
                description="View below the great card packs available for purchase! One purchase is 3 Cards!",
            )
        )

        try:
            user_page = botapp.d['pokestore_page_cache'][int(user_id)]
        except KeyError:
            botapp.d['pokestore_page_cache'][int(user_id)] = 1
            user_page = 1

        page_stock = botapp.d['pokeshop']['stock'][user_page]['pack']

        stock_txt = ""
        stock_item_ids = []
        for item in page_stock:
            stock_txt += f"{item['identifier']} - {item['name']}\n{rarity_crossref[item['rarity']]}\n"
            stock_item_ids.append(item['identifier'])

        stock_txt += (f"\n**PRICE: {botapp.d['pokeshop']['stock'][user_page]['price']} POKECOINS**\n\n"
                      f"*To buy this, use the command:*\n"
                      f"*/pokeshop buy {user_page}*")

        embed.add_field(
            f"Card Pack {user_page}",
            stock_txt,
        )

        # Loads the byte data for the cards
        img_bytes_list = []
        for item_id in stock_item_ids:
            img_bytes_list.append(dbcards.load_img_bytes(item_id))

        # Combines the images
        image = combine_image(img_bytes_pack=img_bytes_list)

        embed.set_image(image)

        return embed

    @staticmethod
    def init_view():
        # noinspection PyUnusedLocal
        class Menu_Init(miru.View):
            @miru.button(label="Back", emoji="⬅️", style=hikari.ButtonStyle.SECONDARY)
            async def back_btn(self, ctx: miru.ViewContext, button: miru.Button) -> None:
                botapp.d['pokestore_page_cache'][int(ctx.author.id)] -= 1
                embed = main_view.gen_embed(ctx.author.id)
                await ctx.edit_response(embed=embed)

            @miru.button(label="Next", emoji="➡️", style=hikari.ButtonStyle.PRIMARY)
            async def next_btn(self, ctx: miru.ViewContext, button: miru.Button) -> None:
                botapp.d['pokestore_page_cache'][int(ctx.author.id)] += 1
                embed = main_view.gen_embed(ctx.author.id)
                await ctx.edit_response(embed=embed)

            # noinspection PyUnusedLocal
            @miru.button(label="Stop Browsing", style=hikari.ButtonStyle.DANGER)
            async def stop_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
                botapp.d['pokestore_page_cache'][int(ctx.author.id)] = 1
                await ctx.edit_response(
                    embed=main_view.gen_embed(ctx.author.id),
                    components=[],
                )
                self.stop()  # Called to stop the view

        menu = Menu_Init()

        return menu