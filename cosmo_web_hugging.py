from gradio_client import Client





async def send_post_request():
    client = Client("chohj06ms/cosmo_token_generater")
    result = client.predict(
        api_name="/main"
    )
    print(result)
    return result

