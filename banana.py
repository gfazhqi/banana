import aiohttp
from colorama import Fore, Style
from datetime import datetime
from fake_useragent import FakeUserAgent
import pytz


def print_timestamp(message, timezone='Asia/Jakarta'):
    local_tz = pytz.timezone(timezone)
    now = datetime.now(local_tz)
    timestamp = now.strftime(f'%x %X %Z')
    print(
        f"{Fore.BLUE + Style.BRIGHT}[ {timestamp} ]{Style.RESET_ALL}"
        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
        f"{message}"
    )


class Banana:
    def __init__(self):
        self.headers = {
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

    async def fetch(self, session, url, method='GET', token=None, payload=None):
        headers = self.headers.copy()
        if token:
            headers['Authorization'] = token
        
        async with session.request(method, url, headers=headers, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def get_user_info(self, session, token):
        url = 'https://interface.carv.io/banana/get_user_info'
        return await self.fetch(session, url, token=token)

    async def get_lottery_info(self, session, token):
        url = 'https://interface.carv.io/banana/get_lottery_info'
        try:
            get_user = await self.get_user_info(session, token)
            data = await self.fetch(session, url, token=token)

            if get_user['data']['max_click_count'] > get_user['data']['today_click_count']:
                click = await self.do_click(session, token, get_user['data']['max_click_count'] - get_user['data']['today_click_count'])
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
                claim_lottery = await self.claim_lottery(session, token, lottery_type=1)
                if claim_lottery['msg'] == "Success":
                    print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Lottery Claimed 🍌 ]{Style.RESET_ALL}")
                else:
                    print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {claim_lottery['msg']} ]{Style.RESET_ALL}")
            
            get_lottery = await self.get_user_info(session, token)
            harvest = get_lottery['data']['lottery_info']['remain_lottery_count']
            while harvest > 0:
                await self.do_lottery(session, token)
                harvest -= 1
        except (Exception, aiohttp.ClientError) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    async def do_click(self, session, token, click_count):
        url = 'https://interface.carv.io/banana/do_click'
        payload = {'clickCount': click_count}
        return await self.fetch(session, url, method='POST', token=token, payload=payload)

    async def claim_lottery(self, session, token, lottery_type):
        url = 'https://interface.carv.io/banana/claim_lottery'
        payload = {'claimLotteryType': lottery_type}
        return await self.fetch(session, url, method='POST', token=token, payload=payload)

    async def do_lottery(self, session, token):
        url = 'https://interface.carv.io/banana/do_lottery'
        data = await self.fetch(session, url, method='POST', token=token)
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

    async def get_banana_list(self, session, token):
        url = 'https://interface.carv.io/banana/get_banana_list'
        try:
            get_user = await self.get_user_info(session, token)
            get_banana = await self.fetch(session, url, token=token)
            filtered_banana_list = [banana for banana in get_banana['data']['banana_list'] if banana['count'] >= 1]
            highest_banana = max(filtered_banana_list, key=lambda x: x['banana_id'])
            if highest_banana['banana_id'] > get_user['data']['equip_banana']['banana_id']:
                print_timestamp(f"{Fore.MAGENTA + Style.BRIGHT}[ Equipping Banana ]{Style.RESET_ALL}")
                equip_banana = await self.do_equip(session, token, highest_banana['banana_id'])
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
                sell_banana = await self.do_sell(session, token, sell['banana_id'], sell['count'] - 1)
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
        except (Exception, aiohttp.ClientError) as e:
            return print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")

    async def do_equip(self, session, token, banana_id):
        url = 'https://interface.carv.io/banana/do_equip'
        payload = {'bananaId': banana_id}
        return await self.fetch(session, url, method='POST', token=token, payload=payload)

    async def do_sell(self, session, token, banana_id, sell_count):
        url = 'https://interface.carv.io/banana/do_sell'
        payload = {'bananaId': banana_id, 'sellCount': sell_count}
        return await self.fetch(session, url, method='POST', token=token, payload=payload)