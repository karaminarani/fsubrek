from bot.utils.db import Database
from bot.utils.logger import Logger
from config import Config


class Cache:
    def __init__(self, db: Database):
        self.db = db
        self.datas = None

    async def fetching(self):
        self.clear()
        await self.relown()
        self.datas = await self.gvars()
        Logger.info('Mongo Database Fetched')

    def clear(self):
        self.datas = None

    async def gvars(self):
        return await self.db.gvars('BOT_VARS')
    
    async def admnvar(self):
        bvars = await self.gvars()
        return bvars.get('ADMIN_IDS', [])
    
    async def relown(self):
        owner = Config.OWNER_ID
        admns = await self.admnvar()
        if owner not in admns:
            await self.db.invar(
            'BOT_VARS',
            'ADMIN_IDS',
            owner,
        )

    @property
    def vars(self):
        return self.datas


Cache = Cache(Database)