from motor.motor_asyncio import AsyncIOMotorClient

from config import Config


class Database:
    Client = AsyncIOMotorClient(Config.MONGO_URL)

    def __init__(self):
        self.mongo = self.Client[Config.BOT_ID]
        self.bvars = self.mongo['bvars']
        self.users = self.mongo['users']
        self.rstrt = self.mongo['rstrt']

    async def gvars(self, _id: str | int) -> any:
        return await self.bvars.find_one({'_id': _id})

    async def invar(
        self,
        _id: str | int,
        field: str,
        value: str | int,
    ) -> any:
        await self.bvars.update_one(
            {'_id': _id},
            {'$addToSet': {field: value}},
            upsert=True,
        )

    async def rmvar(
        self,
        _id: str | int,
        field: str,
        value: str | int,
    ) -> any:
        await self.bvars.update_one(
            {'_id': _id},
            {'$pull': {field: value}},
        )

    async def outvars(
        self,
        _id: str | int,
        field: str,
    ) -> any:
        await self.bvars.update_one(
            {'_id': _id},
            {'$unset': {field: ''}},
        )

    async def gusrs(self) -> list[int] | None:
        pipe = [{'$project': {'_id': 1}}]
        crsr = self.users.aggregate(pipe)
        return [document['_id'] async for document in crsr]

    async def inusr(self, user: int) -> None:
        await self.users.update_one(
            {'_id': user},
            {'$setOnInsert': {'_id': user}},
            upsert=True,
        )

    async def rmusr(self, user: int) -> None:
        await self.users.delete_one({'_id': user})

    async def inmsg(
        self, msg: str, cid: int, mid: int,
    ) -> None:
        await self.rstrt.insert_one(
            {
                '_id': msg,
                'cid': cid,
                'mid': mid,
            },
        )

    async def gmsgs(self, msg: str) -> dict | None:
        return await self.rstrt.find_one(
            {'_id': msg},
        )

    async def rmmsg(self, msg: str) -> None:
        await self.rstrt.delete_one({'_id': msg})


Database = Database()
