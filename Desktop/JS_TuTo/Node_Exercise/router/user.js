import express from 'express'
import prisma from '../prismaClient.js'
import multer from 'multer'
import bcrypt from 'bcrypt'
import jwt from 'jsonwebtoken'
import authModule from '../middlewares/auth.js';
import removeOldTokens from '../middlewares/tokenRemove.js'

const { auth } = authModule;

const router = express.Router()
const upload = multer()

router.get("/users", async(req, res) => {
    try {
        const data = await prisma.user.findMany({
            include: {
                posts: true,
                comments: true,
                friends: true,
                followers: true,
                following: true
            },
            orderBy: {
                id: 'desc'
            },
            take: 20
        })
        res.json(data)
    } catch (e) {
        res.status(500).json({ error: e })
    }
})

router.get("/users/:id", async(req, res) => {
    try {
        const { id } = req.params
        const data = await prisma.user.findFirst({
            where: {
                id: Number(id)
            },
            include: {
                posts: true,
                comments: true,
                friends: true,
                followers: true,
                following: true
            }
        })
        res.json(data)
    } catch (e) {
        res.status(500).json({ error: e })
    }
})

router.get("/search", async(req, res) => {
    const { q } = req.params;

    const data = await prisma.user.findMany({
        where: {
            name: {
                contains: q,
            },
        },
        include: {
            friends: true,
            followers: true,
            following: true
        },
        take: 20
    });
    res.json(data)
})

router.post("/users", upload.none(), async(req, res) => {
    try {
        const { name, username, bio, password } = req.body;

        if (!name || !username || !bio || !password) {
            return res.status(400).json({ msg: "Name, username, bio, and password are required." });
        }

        const hashpassword = await bcrypt.hash(password, 10);
        const user = await prisma.user.create({
            data: {
                name,
                username,
                bio,
                password: hashpassword
            }
        });

        return res.json(user);
    } catch (e) {
        // Log the error for debugging purposes
        console.error(e);

        // Send a proper JSON response
        return res.status(500).json({ error: e.message });
    }
});

router.post("/login", upload.none(), async(req, res) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return res
            .status(400)
            .json({ msg: "username and password required" })
    }

    const user = await prisma.user.findUnique({
        where: { username },
    });

    if (user) {
        if (bcrypt.compare(password, user.password)) {
            const token = jwt.sign(user, process.env.JWT_SECRET);
            await prisma.token.create({
                data: {
                    usertoken: token,
                    userId: user.id
                }
            })
            return res.json({ token, user })
        }
    }

    res.status(401).json({ msg: "incorrect username and password" })
});

router.post("/logout", auth, async(req, res) => {
    try {
        const user = res.locals.user;

        await prisma.token.deleteMany({
            where: {
                userId: Number(user.id)
            }
        });

        res.json({ msg: 'Logged out successfully' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: error.message });
    }
});


router.post("/follow/:id", auth, async(req, res) => {
    const user = res.locals.user;
    const { id } = req.params;

    const data = await prisma.follow.create({
        data: {
            follower: Number(user.id),
            followingId: Number(id),
        }
    });
    res.json(data);
})

router.delete("/unfollow/:id", auth, async(req, res) => {
    const user = res.locals.user;
    const { id } = req.params;

    await prisma.follow.deleteMany({
        where: {
            followerId: Number(user.id),
            followingId: Number(id),
        }
    })

    res.json({ msg: `Unfollow user ${id}` });
})

router.post("/friends/:id", upload.none(), auth, async(req, res) => {
    const user = res.locals.user;
    const { id } = req.params;
    const { statusId } = req.body;

    const friends = await prisma.friend.create({
        data: {
            userId: Number(user.id),
            friendId: Number(id),
            friendRequestStatusId: Number(statusId),
        }
    })

    res.json(friends);
})

router.delete("/unfriends/:id", auth, async(req, res) => {
    const user = res.locals.user;
    const { id } = req.params;
    const { statusId } = req.body;

    await prisma.friend.deleteMany({
        userId: Number(user.id),
        friendId: Number(id),
        friendRequestStatusId: Number(statusId)
    })

    res.json({
        msg: `Unfriend user ${id}`
    })
})

router.post('/cleanup-tokens', upload.none(), async(req, res) => {
    try {
        await removeOldTokens();
        res.json({ msg: 'Old tokens removed successfully' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: error.message });
    }
});

router.get("/verify", auth, async(req, res) => {
    const user = res.locals.user;
    res.json(user);
})

export default router