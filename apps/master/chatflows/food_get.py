
def chat(bot):
    """
    to call this something like localhost:3000/bot/order_my_food will be called on webserver
    """
    
    s = bot.string_ask("please fill in")
    i = bot.int_ask("please fill in int")

    if i == 1:
        i+=1

    bot.md_show("#header 1\n\n- %s"%i)
