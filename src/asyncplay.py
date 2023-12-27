import asyncio


# First layer of async generator
async def generator1():
    for i in range(5):
        yield i


# Second layer of async generator
async def generator2(gen):
    async for item in gen:
        yield item * 2


# Third layer of async generator
async def generator3(gen):
    async for item in gen:
        yield item + 1


# Main async function to chain generators and print results
async def main():
    gen1 = generator1()
    gen2 = generator2(gen1)
    gen3 = generator3(gen2)

    async for item in gen3:
        print(item)  # Print statement showing the working of all generators


# Run the main async function
asyncio.run(main())
