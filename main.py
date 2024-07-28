from banana import Banana, print_timestamp
from colorama import Fore, Style, init
from time import sleep
import sys


def main():
    init(autoreset=True)

    ban = Banana()
    tokens = ban.login()

    for index, token in enumerate(tokens):
        get_user = ban.get_user_info(token=token)
        print_timestamp(
            f"{Fore.CYAN + Style.BRIGHT}[ {get_user['data']['username']} 🤖 ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.YELLOW + Style.BRIGHT}[ Peel {get_user['data']['peel']} 🍌 ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.GREEN + Style.BRIGHT}[ USDT {get_user['data']['usdt']} 🤑 ]{Style.RESET_ALL}"
        )
        ban.get_lottery_info(token=token)
        ban.get_banana_list(token=token)
        print_timestamp(f"{Fore.WHITE + Style.BRIGHT}=-={Style.RESET_ALL}" * 10)

    for _ in range(5 * 3600, 0, -1):
        hours, remainder = divmod(_, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"{Fore.YELLOW + Style.BRIGHT}[ {int(hours)} Hours {int(minutes)} Minutes {int(seconds)} Seconds Remaining To Process All Account ]{Style.RESET_ALL}", end="\r", flush=True)
        sleep(1)

    print()


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")
        except KeyboardInterrupt:
            sys.exit(0)