from pyrogram.errors import RPCError
from pyrogram.helpers import ikb
from pyrogram.types import Message

from bot.client import Bot


class Helpers:
    cacheids = {}

    def __init__(self, Client: Bot):
        self._client_ = Client
        self.protectc = False
        self.generate = False
        self.adminids = []
        self.fsubcids = []
        self.startmsg = None
        self.forcemsg = None

    def gvars(self, vari: str, default=None):
        return self._client_.var.vars.get(vari, default)

    def initializing(self):
        self.fsubcids = self.gvars('FSUB_IDS', [])
        self.protectc = self.gvars('PROTECT_CONTENT', [])[0]
        self._client_.log.info('Protect Content Initialized')
        self.adminids = self.gvars('ADMIN_IDS', [])
        self._client_.log.info('Admins Initialized')
        self.startmsg = self.gvars('START_MESSAGE', [])[0]
        self._client_.log.info('Start Text Initialized')
        self.forcemsg = self.gvars('FORCE_MESSAGE', [])[0]
        self._client_.log.info('Force Text Initialized')
        self.generate = self.gvars('GEN_STATUS', [])[0]
        self._client_.log.info('Generator Initialized')

    def urlikb(self, text: str, url: str) -> ikb:
        return ikb([[(text, url, 'url')]])

    def urlstr(self, string: str, share=False) -> str:
        if share:
            return f'https://t.me/share/url?url={string}'
        return f'https://t.me/{self._client_.me.username}?start={string}'
    
    @property
    def clear(self):
        self.cacheids = {}

    def reload(self):
        self.clear
        return self.initializing()

    async def cached(self):
        self.reload()
        if not self.fsubcids:
            return None
        for i, cid in enumerate(self.fsubcids):
            try:
                gchat = await self._client_.get_chat(cid)
                ctype = gchat.type.value
                title = 'Group' if ctype in [
                    'group',
                    'supergroup',
                ] else 'Channel'
                ilink = gchat.invite_link
                self.cacheids[cid] = {
                    'title': title,
                    'ilink': ilink,
                }
                self._client_.log.info(f'FSub-{i + 1} Initialized')
            except RPCError as e:
                self._client_.log.warning(f'FSub-{i + 1}: {e}')

    async def usrikb(self, message: Message, user: int):
        nojoin = await self.nojoin(user)
        if not self.fsubcids or not nojoin:
            return None
        buttons = []
        for cid in nojoin:
            title = self.cacheids[cid]['title']
            ilink = self.cacheids[cid]['ilink']
            buttons.append((f'Join {title}', ilink, 'url'))
        layouts = [
            buttons[i: i + 2]
            for i in range(0, len(buttons), 2)
        ]
        if len(message.command) > 1:
            layouts.append(
                [
                    (
                        'Try Again',
                        self.urlstr(message.command[1]),
                        'url',
                    ),
                ],
            )
        return ikb(layouts)

    async def nojoin(self, user: int) -> list[int] | None:
        joined = set()
        if not self.fsubcids or user in self.adminids:
            return None
        for cid in self.fsubcids:
            try:
                await self._client_.get_chat_member(cid, user)
                joined.add(cid)
            except RPCError:
                continue
        return [
            cid for cid in self.fsubcids
            if cid not in joined
        ]

    def encode(self, first: int, last: int) -> str:
        _data = first * abs(self._client_.env.DATABASE_ID)
        data_ = last * abs(self._client_.env.DATABASE_ID)
        return self._client_.url.encode(f'id-{_data}-{data_}')

    def decode(self, string: str) -> list[int] | range:
        dbchid = self._client_.env.DATABASE_ID
        decode = self._client_.url.decode(string).split('-')
        if len(decode) == 2:
            return [int(int(decode[1]) / abs(dbchid))]
        elif len(decode) == 3:
            start = int(int(decode[1]) / abs(dbchid))
            end = int(int(decode[2]) / abs(dbchid))
            return range(start, end + 1) if start < end \
                else range(start, end - 1, -1)

    async def getmsgs(self, ids: int):
        return await self._client_.get_messages(
            self._client_.env.DATABASE_ID,
            ids,
        )

    async def copymsgs(self, msg: Message, user: int):
        await msg.copy(
            user,
            protect_content=self.protectc,
        )

    async def copymsg(self, msg: Message) -> int:
        copied = await msg.copy(
            self._client_.env.DATABASE_ID,
            disable_notification=True,
        )
        return copied.id

    def admikb(self) -> None:
        buttons = []
        if self.fsubcids:
            for cid in self.fsubcids:
                title = self.cacheids[cid]['title']
                ilink = self.cacheids[cid]['ilink']
                buttons.append((title, ilink, 'url'))
        layouts = [
            buttons[i: i + 3]
            for i in range(0, len(buttons), 3)
        ]
        layouts.append(
            [
                ('Configuration', 'home-home'),
            ],
        )
        return ikb(layouts)


helpers = Helpers(Bot)


class Filter:
    def decorator(self, func):
        async def wrapped(client, event):
            if hasattr(event, 'from_user'):
                user = event.from_user.id
            elif hasattr(event, 'message') and hasattr(event.message, 'chat'):
                user = event.message.chat.id
            else:
                return
            if user not in helpers.adminids:
                return
            await func(client, event)
        return wrapped

    def Admins(self, func):
        return self.decorator(func)


Filter = Filter()


class Markup:
    HOME = [
        [
            ('Generate Controller', 'set-gen'),
        ],
        [
            ('Start Text', 'set-strtmsg'),
            ('Force Text', 'set-frcmsg'),
        ],
        [
            ('Protect Content', 'set-prtctcntnt'),
        ],
        [
            ('Admin IDs', 'set-admnids'),
            ('FSub IDs', 'set-fscids'),
        ],
        [
            ('Monitor and Stats', 'home-stats'),
        ],
        [
            ('Close', 'home-close'),
        ],
    ]

    STATS = [
        [
            ('Broadcast', 'stats-bc'),
        ],
        [
            ('Ping', 'stats-ping'),
            ('Users', 'stats-users'),
        ],
        [
            ('« Back', 'home-home'),
        ],
    ]

    BACK = [
        [
            ('« Back', 'home-home'),
        ],
    ]

    SET_ADMIN = [
        [
            ('Add User', 'add-admnids'),
            ('Del User', 'del-admnids'),
        ],
        [
            ('« Back', 'home-home'),
        ],
    ]

    SET_FSUB = [
        [
            ('Add Chat', 'add-fscids'),
            ('Del Chat', 'del-fscids'),
        ],
        [
            ('« Back', 'home-home'),
        ],
    ]

    SET_PROTECT = [
        [
            ('« Back', 'home-home'),
            ('Change', 'change-prtctcntnt'),
        ],
    ]

    SET_GENERATOR = [
        [
            ('« Back', 'home-home'),
            ('Change', 'change-gen'),
        ],
    ]

    SET_START = [
        [
            ('« Back', 'home-home'),
            ('Change', 'change-strtmsg'),
        ],
    ]

    SET_FORCE = [
        [
            ('« Back', 'home-home'),
            ('Change', 'change-frcmsg'),
        ],
    ]

    BROADCAST_STATS = [
        [
            ('Stop', 'bc-abort'),
            ('Ref.', 'bc-refresh'),
        ],
    ]


Markup = Markup()