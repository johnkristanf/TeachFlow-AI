async def retry_message_queue(message, retries):
    await message.reject(requeue=False)
    exchange = await message.channel.get_exchange("")
    await exchange.publish(
        message.clone(headers={**message.headers, "x-retry": retries + 1}),
        routing_key=message.routing_key,
    )
