from colorama import Fore, Style, init
from datetime import datetime
from fake_useragent import FakeUserAgent
import aiohttp
import asyncio
import pytz
import sys


def print_timestamp(message, timezone='Asia/Jakarta'):
    local_tz = pytz.timezone(timezone)
    now = datetime.now(local_tz)
    timestamp = now.strftime(f'%x %X %Z')
    print(
        f"{Fore.BLUE + Style.BRIGHT}[ {timestamp} ]{Style.RESET_ALL}"
        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
        f"{message}"
    )

HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Host': 'interface.carv.io',
    'Origin': 'https://banana.carv.io',
    'Referer': 'https://banana.carv.io/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': FakeUserAgent().random,
    'x-app-id': 'carv'
}

async def get_user_info(session, token: str):
    url = 'https://interface.carv.io/banana/get_user_info'
    headers = HEADERS.copy()
    headers.update({'Authorization': token})
    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        return await response.json()

async def get_lottery_info(session, token: str):
    url = 'https://interface.carv.io/banana/get_lottery_info'
    headers = HEADERS.copy()
    headers.update({'Authorization': token})
    get_user = await get_user_info(session, token)
    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        data = await response.json()
        
        if get_user['data']['max_click_count'] > get_user['data']['today_click_count']:
            click = await do_click(session, token, get_user['data']['max_click_count'] - get_user['data']['today_click_count'])
            if click['msg'] == "Success":
                print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Clicked {click['data']['peel']} 🍌 ]{Style.RESET_ALL}")
            else:
                print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {click['msg']} ]{Style.RESET_ALL}")
        else:
            print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Out Of Clicks, Banana Break 😋 ]{Style.RESET_ALL}")

        now = datetime.now()
        last_countdown_start_time = datetime.fromtimestamp(data['data']['last_countdown_start_time'] / 1000)
        countdown_interval_minutes = data['data']['countdown_interval']

        elapsed_time_minutes = (now - last_countdown_start_time).total_seconds() / 60
        remaining_time_minutes = max(countdown_interval_minutes - elapsed_time_minutes, 0)
        if remaining_time_minutes > 0 or data['data']['countdown_end'] == False:
            hours, remainder = divmod(remaining_time_minutes * 60, 3600)
            minutes, seconds = divmod(remainder, 60)
            print_timestamp(f"{Fore.BLUE + Style.BRIGHT}[ Claim Your Banana In {int(hours)} Hours {int(minutes)} Minutes {int(seconds)} Seconds ]{Style.RESET_ALL}")
        else:
            claim_lottery = await claim_lottery(session, token, lottery_type=1)
            if claim_lottery['msg'] == "Success":
                print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Lottery Claimed 🍌 ]{Style.RESET_ALL}")
            else:
                print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {claim_lottery['msg']} ]{Style.RESET_ALL}")
        
        get_lottery = await get_user_info(session, token)
        harvest = get_lottery['data']['lottery_info']['remain_lottery_count']
        while harvest > 0:
            await do_lottery(session, token)
            harvest -= 1

async def do_click(session, token: str, click_count: int):
    url = 'https://interface.carv.io/banana/do_click'
    headers = HEADERS.copy()
    headers.update({'Authorization': token})
    payload = {'clickCount': click_count}
    async with session.post(url, headers=headers, json=payload) as response:
        response.raise_for_status()
        return await response.json()

async def claim_lottery(session, token: str, lottery_type: int):
    url = 'https://interface.carv.io/banana/claim_lottery'
    headers = HEADERS.copy()
    headers.update({'Authorization': token})
    payload = {'claimLotteryType': lottery_type}
    async with session.post(url, headers=headers, json=payload) as response:
        response.raise_for_status()
        return await response.json()

async def do_lottery(session, token: str):
    url = 'https://interface.carv.io/banana/do_lottery'
    headers = HEADERS.copy()
    headers.update({'Authorization': token})
    async with session.post(url, headers=headers, json={}) as response:
        response.raise_for_status()
        data = await response.json()
        if data['msg'] == "Success":
            print_timestamp(
                f"{Fore.YELLOW + Style.BRIGHT}[ {data['data']['name']} 🍌 ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}[ Ripeness {data['data']['ripeness']} ]{Style.RESET_ALL}"
            )
            print_timestamp(f"{Fore.BLUE + Style.BRIGHT}[ Daily Peel Limit {data['data']['daily_peel_limit']} ]{Style.RESET_ALL}")
            print_timestamp(
                f"{Fore.YELLOW + Style.BRIGHT}[ Sell Price Peel {data['data']['sell_exchange_peel']} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT}[ Sell Price USDT {data['data']['sell_exchange_usdt']} ]{Style.RESET_ALL}"
            )
        else:
            print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {data['msg']} ]{Style.RESET_ALL}")

async def get_banana_list(session, token: str):
    url = 'https://interface.carv.io/banana/get_banana_list'
    headers = HEADERS.copy()
    headers.update({'Authorization': token})
    get_user = await get_user_info(session, token)
    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        get_banana = await response.json()
        filtered_banana_list = [banana for banana in get_banana['data']['banana_list'] if banana['count'] >= 1]
        highest_banana = max(filtered_banana_list, key=lambda x: x['banana_id'])
        if highest_banana['banana_id'] > get_user['data']['equip_banana']['banana_id']:
            print_timestamp(f"{Fore.MAGENTA + Style.BRIGHT}[ Equipping Banana ]{Style.RESET_ALL}")
            equip_banana = await do_equip(session, token, highest_banana['banana_id'])
            if equip_banana['msg'] == "Success":
                print_timestamp(
                    f"{Fore.YELLOW + Style.BRIGHT}[ {highest_banana['name']} 🍌 ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}[ Ripeness {highest_banana['ripeness']} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT}[ Daily Peel Limit {highest_banana['daily_peel_limit']} ]{Style.RESET_ALL}"
                )
            else:
                print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {equip_banana['msg']} ]{Style.RESET_ALL}")
        else:
            print_timestamp(f"{Fore.MAGENTA + Style.BRIGHT}[ Currently Using ]{Style.RESET_ALL}")
            print_timestamp(
                f"{Fore.YELLOW + Style.BRIGHT}[ {highest_banana['name']} 🍌 ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}[ Ripeness {highest_banana['ripeness']} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}[ Daily Peel Limit {highest_banana['daily_peel_limit']} ]{Style.RESET_ALL}"
            )
        count_banana = [banana for banana in get_banana['data']['banana_list'] if banana['count'] > 1]
        for sell in count_banana:
            sell_banana = await do_sell(session, token, sell['banana_id'], sell['count'] - 1)
            if sell_banana['msg'] == "Success":
                print_timestamp(f"{Fore.MAGENTA + Style.BRIGHT}[ Only One {sell['name']} Remaining ]{Style.RESET_ALL}")
                print_timestamp(
                    f"{Fore.YELLOW + Style.BRIGHT}[ Sell Got {sell_banana['data']['sell_got_peel']} Peel 🍌 ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT}[ Sell Got {sell_banana['data']['sell_got_usdt']} USDT 🤑 ]{Style.RESET_ALL}"
                )
                print_timestamp(
                    f"{Fore.YELLOW + Style.BRIGHT}[ {sell_banana['data']['peel']} Peel 🍌 ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT}[ {sell_banana['data']['usdt']} USDT 🤑 ]{Style.RESET_ALL}"
                )
            else:
                print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {sell_banana['msg']} ]{Style.RESET_ALL}")

async def do_equip(session, token: str, banana_id: int):
    url = 'https://interface.carv.io/banana/do_equip'
    headers = HEADERS.copy()
    headers.update({'Authorization': token})
    payload = {'bananaId': banana_id}
    async with session.post(url, headers=headers, json=payload) as response:
        response.raise_for_status()
        return await response.json()

async def do_sell(session, token: str, banana_id: int, sell_count: int):
    url = 'https://interface.carv.io/banana/do_sell'
    headers = HEADERS.copy()
    headers.update({'Authorization': token})
    payload = {'bananaId': banana_id, 'sellCount': sell_count}
    async with session.post(url, headers=headers, json=payload) as response:
        response.raise_for_status()
        return await response.json()

async def main():
    init(autoreset=True)
    tokens = [line.strip() for line in open('tokens.txt', 'r').readlines()]

    async with aiohttp.ClientSession() as session:
        for token in tokens:
            get_user = await get_user_info(session, token)
            print_timestamp(
                f"{Fore.CYAN + Style.BRIGHT}[ {get_user['data']['username']} 🤖 ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}[ Peel {get_user['data']['peel']} 🍌 ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT}[ USDT {get_user['data']['usdt']} 🤑 ]{Style.RESET_ALL}"
            )
            await get_lottery_info(session, token)
            await get_banana_list(session, token)
    
        print_timestamp(f"{Fore.CYAN + Style.BRIGHT}[ Restarting Soon ]{Style.RESET_ALL}")
        await asyncio.sleep(3 * 3600)

if __name__ == '__main__':
    while True:
        try:
            asyncio.run(main())
        except (Exception, aiohttp.ClientResponseError) as e:
            print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")
        except KeyboardInterrupt:
            sys.exit(0)
