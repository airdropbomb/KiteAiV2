from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from aiohttp import ClientResponseError, ClientSession, ClientTimeout
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from colorama import *
from datetime import datetime
import asyncio, binascii, random, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class KiteAi:
    def __init__(self) -> None:
        self.headers = {
            "Accept-Language": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://testnet.gokite.ai",
            "Referer": "https://testnet.gokite.ai/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://testnet.gokite.ai"
        self.NEO_API = "https://neo.prod.gokite.ai/v2"
        self.OZONE_API = "https://ozone-point-system.prod.gokite.ai"
        self.SITE_KEY = "6Lc_VwgrAAAAALtx_UtYQnW-cFg8EPDgJ8QVqkaz"
        self.KEY_HEX = "6a1c35292b7c5b769ff47d89a17e7bc4f0adfe1b462981d28e0e9f7ff20b8f8a"
        self.BITMIND_SUBNET = "0xc368ae279275f80125284d16d292b650ecbbff8d"
        self.BITTE_SUBNET = "0xca312b44a57cc9fd60f37e6c9a343a1ad92a3b6c"
        self.KITE_AI_SUBNET = "0xb132001567650917d6bd695d1fab55db7986e9a5"
        self.CAPTCHA_KEY = None
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.auth_tokens = {}
        self.access_tokens = {}
        self.header_cookies = {}
        self.ai_agents = {}
        self.user_interactions = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
            {Fore.GREEN + Style.BRIGHT}       █████╗ ██████╗ ██████╗     ███╗   ██╗ ██████╗ ██████╗ ███████╗
            {Fore.GREEN + Style.BRIGHT}      ██╔══██╗██╔══██╗██╔══██╗    ████╗  ██║██╔═══██╗██╔══██╗██╔════╝
            {Fore.GREEN + Style.BRIGHT}      ███████║██║  ██║██████╔╝    ██╔██╗ ██║██║   ██║██║  ██║█████╗  
            {Fore.GREEN + Style.BRIGHT}      ██╔══██║██║  ██║██╔══██╗    ██║╚██╗██║██║   ██║██║  ██║██╔══╝  
            {Fore.GREEN + Style.BRIGHT}      ██║  ██║██████╔╝██████╔╝    ██║ ╚████║╚██████╔╝██████╔╝███████╗
            {Fore.GREEN + Style.BRIGHT}      ╚═╝  ╚═╝╚═════╝ ╚═════╝     ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝
            {Fore.YELLOW + Style.BRIGHT}      Modified by ADB NODE
            """
        )

   def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_ai_agents(self):
        filename = "agents.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, token):
        if token not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[token] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[token]

    def rotate_proxy_for_account(self, token):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[token] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy

    def generate_auth_token(self, address):
        try:
            key = bytes.fromhex(self.KEY_HEX)
            iv = os.urandom(12)
            encryptor = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend()).encryptor()

            ciphertext = encryptor.update(address.encode()) + encryptor.finalize()
            auth_tag = encryptor.tag

            result = iv + ciphertext + auth_tag
            result_hex = binascii.hexlify(result).decode()

            return result_hex
        except Exception as e:
            raise Exception(f"Generate Auth Token Failed: {str(e)}")
    
    def generate_quiz_title(self):
        today = datetime.today().strftime('%Y-%m-%d')
        return f"daily_quiz_{today}"
    
    def extract_cookies(self, raw_cookies: list):
        cookies_dict = {}
        try:
            skip_keys = ['expires', 'path', 'domain', 'samesite', 'secure', 'httponly', 'max-age']

            for cookie_str in raw_cookies:
                cookie_parts = cookie_str.split(';')

                for part in cookie_parts:
                    cookie = part.strip()

                    if '=' in cookie:
                        name, value = cookie.split('=', 1)

                        if name and value and name.lower() not in skip_keys:
                            cookies_dict[name] = value

            cookie_header = "; ".join([f"{key}={value}" for key, value in cookies_dict.items()])
            
            return cookie_header
        except Exception as e:
            return None
        
    def setup_ai_agent(self, agents: list):
        agent = random.choice(agents)

        agent_name = agent["agentName"]
        service_id = agent["serviceId"]
        question = random.choice(agent["questionLists"])

        return agent_name, service_id, question
        
    def generate_inference_payload(self, service_id: str, question: str):
        payload = {
            "service_id":service_id,
            "subnet":"kite_ai_labs",
            "stream":True,
            "body":{
                "stream":True,
                "message":question
            }
        }
        return payload
        
    def generate_receipt_payload(self, address: str, service_id: str, question: str, answer: str):
        payload = {
            "address":address,
            "service_id":service_id,
            "input":[{
                "type":"text/plain",
                "value":question
            }],
            "output":[{
                "type":"text/plain",
                "value":answer
            }]
        }
        return payload
    
    def mask_account(self, account):
        mask_account = account[:6] + '*' * 6 + account[-6:]
        return mask_account 
    
    async def print_timer(self, min_delay: int, max_delay: int):
        for remaining in range(random.randint(min_delay, max_delay), 0, -1):
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {remaining} {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Seconds For Next Interaction...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)
    
    def print_question(self):
        while True:
            faucet = input(f"{Fore.YELLOW + Style.BRIGHT}Auto Claim Kite Token Faucet? [y/n] -> {Style.RESET_ALL}").strip()
            if faucet in ["y", "n"]:
                faucet = faucet == "y"
                break
            else:
                print(f"{Fore.RED + Style.BRIGHT}Please enter 'y' or 'n'.{Style.RESET_ALL}")

        if faucet:
            while True:
                capthca_key = input(f"{Fore.YELLOW + Style.BRIGHT}Enter Your 2Captcha Key -> {Style.RESET_ALL}").strip()
                if capthca_key:
                    self.CAPTCHA_KEY = capthca_key
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter your 2captcha key.{Style.RESET_ALL}")

        while True:
            try:
                count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How Many Times Would You Like to Interact With Kite AI Agents? -> {Style.RESET_ALL}").strip())
                if count > 0:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter a positive number.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Monosans Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return faucet, count, choose, rotate
    
    async def solve_recaptcha(self, proxy=None, retries=5):
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:

                    url = f"http://2captcha.com/in.php?key={self.CAPTCHA_KEY}&method=userrecaptcha&googlekey={self.SITE_KEY}&pageurl={self.BASE_API}&json=1"
                    async with session.get(url=url) as response:
                        response.raise_for_status()
                        result = await response.json()

                        if result.get("status") != 1:
                            await asyncio.sleep(5)
                            continue

                        request_id = result.get("request")

                        for _ in range(30):
                            res_url = f"http://2captcha.com/res.php?key={self.CAPTCHA_KEY}&action=get&id={request_id}&json=1"
                            async with session.get(url=res_url) as res_response:
                                res_response.raise_for_status()
                                res_result = await res_response.json()

                                if res_result.get("status") == 1:
                                    recaptcha_token = res_result.get("request")
                                    return recaptcha_token
                                elif res_result.get("request") == "CAPCHA_NOT_READY":
                                    await asyncio.sleep(5)
                                    continue
                                else:
                                    break

            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
        
    async def user_signin(self, address: str, proxy=None, retries=5):
        url = f"{self.NEO_API}/signin"
        data = json.dumps({"eoa":address})
        headers = {
            **self.headers,
            "Authorization": self.auth_tokens[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()

                        raw_cookies = response.headers.getall('Set-Cookie', [])
                        if raw_cookies:
                            cookie_header = self.extract_cookies(raw_cookies)

                            if cookie_header:
                                return result["data"]["access_token"], cookie_header
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None, None
        
    async def user_data(self, address: str, proxy=None, retries=5):
        url = f"{self.OZONE_API}/me"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
        
    async def create_quiz(self, address: str, proxy=None, retries=5):
        url = f"{self.NEO_API}/quiz/create"
        data = json.dumps({"title":self.generate_quiz_title(), "num":1, "eoa":address})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Cookie": self.header_cookies[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
        
    async def get_quiz(self, address: str, quiz_id: int, proxy=None, retries=5):
        url = f"{self.NEO_API}/quiz/get?id={quiz_id}&eoa={address}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Cookie": self.header_cookies[address]
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def submit_quiz(self, address: str, quiz_id: int, question_id: int, quiz_answer: str, proxy=None, retries=5):
        url = f"{self.NEO_API}/quiz/submit"
        data = json.dumps({"quiz_id":quiz_id, "question_id":question_id, "answer":quiz_answer, "finish":True, "eoa":address})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Cookie": self.header_cookies[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def claim_faucet(self, address: str, recaptcha_token: str, proxy=None, retries=5):
        url = f"{self.OZONE_API}/blockchain/faucet-transfer"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length":"2",
            "Content-Type": "application/json",
            "x-recaptcha-token": recaptcha_token
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, json={}) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def token_balance(self, address: str, proxy=None, retries=5):
        url = f"{self.OZONE_API}/me/balance"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def stake_token(self, address: str, amount: float, proxy=None, retries=5):
        url = f"{self.OZONE_API}/subnet/delegate"
        data = json.dumps({"subnet_address":self.KITE_AI_SUBNET, "amount":amount})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def claim_stake_rewards(self, address: str, proxy=None, retries=5):
        url = f"{self.OZONE_API}/subnet/claim-rewards"
        data = json.dumps({"subnet_address":self.KITE_AI_SUBNET})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def agent_inference(self, address: str, service_id: str, question: str, proxy=None, retries=5):
        url = f"{self.OZONE_API}/agent/inference"
        data = json.dumps(self.generate_inference_payload(service_id, question))
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = ""

                        async for line in response.content:
                            line = line.decode("utf-8").strip()
                            if line.startswith("data:"):
                                try:
                                    json_data = json.loads(line[len("data:"):].strip())
                                    delta = json_data.get("choices", [{}])[0].get("delta", {})
                                    content = delta.get("content")
                                    if content:
                                        result += content
                                except json.JSONDecodeError:
                                    continue

                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def submit_receipt(self, address: str, sa_address: str, service_id: str, question: str, answer: str, proxy=None, retries=5):
        url = f"{self.NEO_API}/submit_receipt"
        data = json.dumps(self.generate_receipt_payload(sa_address, service_id, question, answer))
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Cookie": self.header_cookies[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def process_user_signin(self, address: str, use_proxy: bool, rotate_proxy: bool):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.YELLOW + Style.BRIGHT}Try To Login, Wait...{Style.RESET_ALL}",
            end="\r",
            flush=True
        )

        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        if rotate_proxy:
            access_token = None
            header_cookie = None
            while access_token is None or header_cookie is None:
                access_token, header_cookie = await self.user_signin(address, proxy)
                if not access_token or not header_cookie:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Login Failed {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Rotating Proxy {Style.RESET_ALL}"
                    )
                    proxy = self.rotate_proxy_for_account(address) if use_proxy else None
                    await asyncio.sleep(5)
                    continue

                self.access_tokens[address] = access_token
                self.header_cookies[address] = header_cookie

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Login Success {Style.RESET_ALL}                  "
                )
                return True

        access_token, header_cookie = await self.user_signin(address, proxy)
        if not access_token or not header_cookie:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Login Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} Skipping This Account {Style.RESET_ALL}"
            )
            return False
        
        self.access_tokens[address] = access_token
        self.header_cookies[address] = header_cookie
        
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} Login Success {Style.RESET_ALL}                  "
        )
        return True
        
    async def process_accounts(self, address: str, agents: list, faucet: bool, interact_count: int, use_proxy: bool, rotate_proxy: bool):
        signed = await self.process_user_signin(address, use_proxy, rotate_proxy)
        if signed:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )
        
            user = await self.user_data(address, proxy)
            if not user:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET User Data Failed {Style.RESET_ALL}"
                )
                return
            
            username = user.get("data", {}).get("profile", {}).get("username", "Unknown")
            sa_address = user.get("data", {}).get("profile", {}).get("smart_account_address", "Undifined")
            balance = user.get("data", {}).get("profile", {}).get("total_xp_points", 0)
            
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Username  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {username} {Style.RESET_ALL}"
            )
            
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}SA Address:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.mask_account(sa_address)} {Style.RESET_ALL}"
            )
            self.log(f"{Fore.CYAN+Style.BRIGHT}Balance   :{Style.RESET_ALL}")

            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}  ● {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} XP {Style.RESET_ALL}"
            )

            kite_balance = "N/A"
            usdt_balance = "N/A"

            balance = await self.token_balance(address, proxy)
            if balance:
                kite_balance = balance.get("data", ).get("balances", {}).get("kite", 0)
                usdt_balance = balance.get("data", ).get("balances", {}).get("usdt", 0)

            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}  ● {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {kite_balance} KITE {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}  ● {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {usdt_balance} USDT {Style.RESET_ALL}"
            )

            if faucet:
                is_claimable = user.get("data", {}).get("faucet_claimable", False)

                if is_claimable:
                    self.log(f"{Fore.CYAN+Style.BRIGHT}Faucet    :{Style.RESET_ALL}")
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE + Style.BRIGHT}Wait For Solving Captcha...{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )

                    recaptcha_token = await self.solve_recaptcha(proxy)
                    if recaptcha_token:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}  ● {Style.RESET_ALL}"
                            f"{Fore.BLUE + Style.BRIGHT}Captcha :{Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT} Solved {Style.RESET_ALL}                 "
                        )

                        claim = await self.claim_faucet(address, recaptcha_token, proxy)
                        if claim:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}  ● {Style.RESET_ALL}"
                                f"{Fore.BLUE + Style.BRIGHT}Status  :{Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT} Claimed Successfully {Style.RESET_ALL}"
                            )
                        else:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}  ● {Style.RESET_ALL}"
                                f"{Fore.BLUE + Style.BRIGHT}Status  :{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Not Claimed {Style.RESET_ALL}"
                            )
                    else:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}  ● {Style.RESET_ALL}"
                            f"{Fore.BLUE + Style.BRIGHT}Captcha :{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} Unsolved {Style.RESET_ALL}                 "
                        )
                else:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Faucet    :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Not Time to Claim {Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Faucet    :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Skipping Claim {Style.RESET_ALL}"
                )

            create = await self.create_quiz(address, proxy)
            if create:
                self.log(f"{Fore.CYAN+Style.BRIGHT}Daily Quiz:{Style.RESET_ALL}")

                quiz_id = create.get("data", {}).get("quiz_id")
                status = create.get("data", {}).get("status")

                if status == 0:
                    quiz = await self.get_quiz(address, quiz_id, proxy)
                    if quiz:
                        quiz_questions = quiz.get("data", {}).get("question", [])

                        if quiz_questions:
                            for quiz_question in quiz_questions:
                                if quiz_question:
                                    question_id = quiz_question.get("question_id")
                                    quiz_content = quiz_question.get("content")
                                    quiz_answer = quiz_question.get("answer")

                                    self.log(
                                        f"{Fore.MAGENTA + Style.BRIGHT}  ● {Style.RESET_ALL}"
                                        f"{Fore.BLUE + Style.BRIGHT}Question:{Style.RESET_ALL}"
                                        f"{Fore.WHITE+Style.BRIGHT} {quiz_content} {Style.RESET_ALL}"
                                    )
                                    self.log(
                                        f"{Fore.MAGENTA + Style.BRIGHT}  ● {Style.RESET_ALL}"
                                        f"{Fore.BLUE + Style.BRIGHT}Answer  :{Style.RESET_ALL}"
                                        f"{Fore.WHITE+Style.BRIGHT} {quiz_answer} {Style.RESET_ALL}"
                                    )

                                    submit_quiz = await self.submit_quiz(address, quiz_id, question_id, quiz_answer, proxy)
                                    if submit_quiz:
                                        result = submit_quiz.get("data", {}).get("result")

                                        if result == "RIGHT":
                                            self.log(
                                                f"{Fore.MAGENTA + Style.BRIGHT}  ● {Style.RESET_ALL}"
                                                f"{Fore.BLUE + Style.BRIGHT}Status  :{Style.RESET_ALL}"
                                                f"{Fore.GREEN+Style.BRIGHT} Answered Successfully {Style.RESET_ALL}"
                                            )
                                        else:
                                            self.log(
                                                f"{Fore.MAGENTA + Style.BRIGHT}  ● {Style.RESET_ALL}"
                                                f"{Fore.BLUE + Style.BRIGHT}Status  :{Style.RESET_ALL}"
                                                f"{Fore.YELLOW+Style.BRIGHT} Wrong Answer {Style.RESET_ALL}"
                                            )
                                    else:
                                        self.log(
                                            f"{Fore.MAGENTA + Style.BRIGHT}  ● {Style.RESET_ALL}"
                                            f"{Fore.BLUE + Style.BRIGHT}Status  :{Style.RESET_ALL}"
                                            f"{Fore.RED+Style.BRIGHT} Submit Answer Failed {Style.RESET_ALL}"
                                        )
                        else:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}  ● {Style.RESET_ALL}"
                                f"{Fore.BLUE + Style.BRIGHT}Status  :{Style.RESET_ALL}"
                                f"{Fore.RED+Style.BRIGHT} GET Quiz Answer Failed {Style.RESET_ALL}"
                            )
                    else:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}  ● {Style.RESET_ALL}"
                            f"{Fore.BLUE + Style.BRIGHT}Status  :{Style.RESET_ALL}"
                            f"{Fore.RED+Style.BRIGHT} GET Quiz Question Failed {Style.RESET_ALL}"
                        )
                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}  ● {Style.RESET_ALL}"
                        f"{Fore.BLUE + Style.BRIGHT}Status  :{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Already Answered {Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Daily Quiz:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET Data Failed {Style.RESET_ALL}"
                )

            kite_balance = 0
            balance = await self.token_balance(address, proxy)
            if balance:
                kite_balance = balance.get("data", ).get("balances", {}).get("kite", 0)

            if kite_balance >= 1:
                amount = float(f"{kite_balance:.1f}")

                stake = await self.stake_token(address, amount, proxy)
                if stake:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Stake     :{Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT} Amount: {Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT}{amount} KITE{Style.RESET_ALL}"
                    )
                else:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Stake     :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Stake     :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficinet Kite Token Balance {Style.RESET_ALL}"
                )

            unstake = await self.claim_stake_rewards(address, proxy)
            if unstake:
                reward = unstake.get("data", {}).get("claim_amount", 0)
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Unstake   :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT} Reward: {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{reward} KITE{Style.RESET_ALL}"
                )
            else:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Unstake   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                )

            self.log(f"{Fore.CYAN+Style.BRIGHT}AI Agents :{Style.RESET_ALL}")

            self.user_interactions[address] = 0

            while self.user_interactions[address] < interact_count:
                self.log(
                    f"{Fore.MAGENTA + Style.BRIGHT}  ● {Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT}Interactions{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {self.user_interactions[address] + 1} of {interact_count} {Style.RESET_ALL}                       "
                )

                agent_name, service_id, question = self.setup_ai_agent(agents)

                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}    Agent Name: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{agent_name}{Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}    Question  : {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{question}{Style.RESET_ALL}"
                )

                answer = await self.agent_inference(address, service_id, question, proxy)
                if answer:
                    self.user_interactions[address] += 1
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}    Answer    : {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{answer.strip()}{Style.RESET_ALL}"
                    )

                    submit = await self.submit_receipt(address, sa_address, service_id, question, answer, proxy)
                    if submit:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}    Status    : {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}Receipt Submited Successfully{Style.RESET_ALL}"
                        )
                    else:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}    Status    : {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}Submit Receipt Failed{Style.RESET_ALL}"
                        )
                else:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}    Status    : {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}Interaction Failed{Style.RESET_ALL}"
                    )

                await self.print_timer(5, 10)

        self.user_interactions[address] = 0

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            agents = self.load_ai_agents()
            if not agents:
                self.log(f"{Fore.RED + Style.BRIGHT}No Agents Loaded.{Style.RESET_ALL}")
                return
            
            faucet, count, use_proxy_choice, rotate_proxy = self.print_question()

            while True:
                use_proxy = False
                if use_proxy_choice in [1, 2]:
                    use_proxy = True

                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies(use_proxy_choice)
                
                separator = "=" * 25
                for address in accounts:
                    if address:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )
                        
                        auth_token = self.generate_auth_token(address)
                        if not auth_token:
                            continue
                        
                        self.auth_tokens[address] = auth_token
                        
                        await self.process_accounts(address, agents, faucet, count, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)
                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except (Exception, ValueError) as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = KiteAi()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Kite Ai Ozone - BOT{Style.RESET_ALL}                                       "                              
        )
