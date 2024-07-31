from banana import Banana, print_timestamp
from colorama import Fore, Style, init
import aiohttp
import asyncio
import sys


async def main():
    init(autoreset=True)

    ban = Banana()
    tokens = [line.strip() for line in open('tokens.txt', 'r').readlines()]

    async with aiohttp.ClientSession() as session:
        for token in tokens:
            get_user = await ban.get_user_info(session, token)
            print_timestamp(
                f"{Fore.CYAN + Style.BRIGHT}[ {get_user['data']['username']} 🤖 ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}[ Peel {get_user['data']['peel']} 🍌 ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT}[ USDT {get_user['data']['usdt']} 🤑 ]{Style.RESET_ALL}"
            )
            await ban.get_lottery_info(session, token)
            await ban.get_banana_list(session, token)

        print_timestamp(f"{Fore.CYAN + Style.BRIGHT}[ Restarting All Account ]{Style.RESET_ALL}")
        await asyncio.sleep(3 * 3600)


if __name__ == '__main__':
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")
        except KeyboardInterrupt:
            sys.exit(0)
