from library.botapp import botapp
import logging

def randomise_stock():
    from library.dbmodules.dbcards import pull_random_card

    # The shop will have at all times 15 possible purchases
    pack_stock = {}
    for pack_id in range(16):  # It would generate to from 1 to 14 if it was set as 15
        card_pack = []
        for b in range(3):
            card = pull_random_card(no_limited=True)
            card_pack.append(card)

        pack_price = (card_pack[0]['rarity'] + card_pack[1]['rarity'] + card_pack[2]['rarity']) * 6 + (card_pack[0]['tier'] + card_pack[1]['tier'] + card_pack[2]['tier'])

        pack_stock[pack_id] = {
            "price": pack_price,
            "pack": card_pack,
            "id": pack_id,
        }

    del b

    botapp.d['pokeshop']['stock'] = pack_stock
    logging.info("PokeShop Stock randomised.")

def buy_pack(pack_id):
    from library.dbmodules import economy

    bought_pack = botapp.d['pokeshop']['stock'][pack_id]
    for card in bought_pack:
        economy.account(card['owner']).pokecoins.modify_balance(card['price'], '+')