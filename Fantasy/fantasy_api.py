import requests

class FantasyAPI:
    def __init__(self, token_file):
        self.token_file = token_file
        self.current_token_index = 0
        self.tokens = self.load_tokens()

    def load_tokens(self):
        with open(self.token_file, 'r') as file:
            return [token.strip() for token in file.readlines()]

    def get_fantasy_token(self):
        return self.tokens[self.current_token_index]

    def get_portfolio_value(self, wallet_address):
        try:
            token = self.get_fantasy_token()
            url = "https://api.fantasy.top/v1/graphql"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "Origin": "https://www.fantasy.top",
                "Referer": "https://www.fantasy.top/",
                "Sec-Ch-Ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": "\"Linux\"",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            }

            payload = {
                "operationName": "GET_PLAYER_BASIC_DATA",
                "query": """
                    query GET_PLAYER_BASIC_DATA($id: String!) {
                      players_by_pk(id: $id) {
                        id
                        name
                        handle
                        fantasy_points
                        fantasy_points_referrals
                        league
                        diamond_tickets
                        gold
                        stars
                        portfolio_value
                        profile_picture
                        number_of_cards: cards_aggregate {
                          aggregate {
                            count(columns: id, distinct: true)
                          }
                        }
                      }
                      rewards(
                        where: {player_id: {_eq: $id}, is_activated: {_eq: true}, _or: [{price: {_eq: 0}}, {price: {_is_null: true}}]}
                      ) {
                        id
                        tournament_id
                      }
                    }
                """,
                "variables": {"id": wallet_address}
            }

            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            if "data" in data and "players_by_pk" in data["data"] and data["data"]["players_by_pk"]:
                portfolio_value = data["data"]["players_by_pk"]["portfolio_value"]
                if portfolio_value is not None:
                    return portfolio_value
            return None
        except requests.RequestException as e:
            print("Error during query execution:", e)
            self.update_token()
            return None
        except KeyError as e:
            print("Error while processing API response:", e)
            return None

    def update_token(self):
        try:
            self.current_token_index = (self.current_token_index + 1) % len(self.tokens)
            new_token = self.get_fantasy_token()
            print("Fantasy API token has been updated:", new_token)
        except Exception as e:
            print("Error when updating Fantasy API token:", e)
            self.current_token_index = 0
            new_token = self.get_fantasy_token()
            print("The first token is used:", new_token)
