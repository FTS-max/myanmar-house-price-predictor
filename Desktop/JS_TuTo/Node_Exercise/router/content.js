import express from 'express'
import prisma from '../prismaClient.js'
import multer from 'multer'
import authModule from '../middlewares/auth.js';

const { auth, isOwner } = authModule;


const router = express.Router();
const upload = multer();

router.get("/posts", async(req, res) => {
    try {
        const data = await prisma.post.findMany({
            include: {
                user: true,
                comments: true,
                Likes: true
            },
            orderBy: {
                id: "desc"
            },
            take: 20
        });
        data.length === '' ? res.sendStatus(404).json({ msg: "Your data not found..." }) : res.json(data)
    } catch (e) {
        res.status(500).json({ error: e })
    }
})

router.get("/posts/:id", async(req, res) => {
    try {
        const { id } = req.params;

        const data = await prisma.post.findFirst({
            where: {
                id: Number(id)
            },
            include: {
                user: true,
                comments: {
                    include: {
                        user: true,
                        Likes: true
                    },
                },
                Likes: true
            }
        })

        res.json(data)
    } catch (e) {
        res.status(500).json({ error: e })
    }
})

router.post("/posts/create", upload.none(), auth, async(req, res) => {
    try {
        const { content, userId } = req.body
        if (!content) {
            return res.status(400).json({ msg: "content required" })
        }

        const user = res.locals.user;
        const post = await prisma.post.create({
            data: {
                content,
                userId: user.id,
            }
        })

        const data = await prisma.post.findUnique({
            where: { id: Number(post.id) },
            include: {
                user: true,
                comments: {
                    include: { user: true },
                }
            }
        })
        res.status(200).json(data)
    } catch (e) {
        res.status(500).json({ error: e })
    }
})

router.get("/posts/edit/:id", async(req, res) => {
    try {
        const { id } = req.params;
        const data = await prisma.post.findFirst({
            where: {
                id: Number(id),
            },
        });

        res.json(data)
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
})

router.put("/posts/update/:id", upload.none(), async(req, res) => {
    try {
        const { id } = req.params;
        const { content, userId } = req.body;

        const post = await prisma.post.findFirst({
            where: {
                id: Number(id),
            },
        });

        if (!post) {
            return res.status(404).json({ error: "Post not found" });
        }

        try {
            const post = await prisma.post.upsert({
                where: { id: id ? Number(id) : -1 }, // Use -1 for new posts without id
                update: {
                    content: content,
                    userId: Number(userId)
                },
                create: {
                    content: content,
                    userId: Number(userId)
                }
            });

            res.status(200).json(post);
        } catch (error) {
            console.error(error);
            res.status(500).json({ error: "An error occurred while creating or updating the post." });
        }
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

router.delete('/posts/delete/:id', auth, isOwner("post"), async(req, res) => {
    try {
        const { id } = req.params;
        const idNumber = Number(id);

        if (isNaN(idNumber) || idNumber <= 0) {
            return res.status(400).json({ error: 'Invalid ID format' });
        }

        // First, delete related comments
        await prisma.comment.deleteMany({
            where: { postId: idNumber }
        });

        // Then delete the post itself
        await prisma.post.delete({
            where: { id: idNumber }
        });

        res.sendStatus(204);
    } catch (e) {
        console.error(e);
        res.status(500).json({ error: e.message });
    }
});

router.get("/comments", async(req, res) => {
    try {
        const data = await prisma.comment.findMany({
            include: {
                user: true,
                post: true
            },
            orderBy: {
                id: 'desc'
            }
        })

        res.json(data)
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
})

router.delete("/comments/delete/:id", auth, isOwner("post"), async(req, res) => {
    const { id } = req.params

    await prisma.comment.delete({
        where: { id: Number(id) }
    })

    res.sendStatus(200)
})

router.post("/comments", auth, async(req, res) => {
    const { content, postId } = req.body

    if (!content || !postId) {
        return
        res.status(400).json({ msg: "content and postId required" })
    }

    const user = res.locals.user

    const comment = await prisma.comment.create({
        data: {
            content,
            userId: Number(user.id),
            postId: Number(postId)
        },
    })

    comment.user = user
    await addNoti({
        type: "comment",
        content: "reply your post",
        postId,
        userId: user.Id
    })

    res.json(comment)
})

router.post("/like/posts/:id", upload.none(), auth, async(req, res) => {
    const { id } = req.params
    const user = res.locals.user;

    const like = await prisma.postLike.create({
        data: {
            postId: Number(id),
            userId: Number(user.id)
        },
    });

    await addNoti({
        type: "like",
        content: "like your post",
        postId,
        userId: user.id
    })

    res.json({ like })
})

router.delete("/unlike/posts/:id", auth, async(req, res) => {
    const { id } = req.params;
    const user = req.locals.user;

    await params.postLike.deleteMany({
        where: {
            postId: Number(id),
            userId: Number(user.id)
        }
    })

    res.json({
        msg: `unlike post ${id}`
    });
})

router.post("/like/comments/:id", upload.none(), auth, async(req, res) => {
    const { id } = req.params;
    const user = res.locals.user;

    const Like = await prisma.commentLike.create({
        data: {
            commentId: Number(id),
            userId: Number(user, id)
        }
    })

    await addNoti({
        type: "like",
        content: "like your comment",
        postId: id,
        userId: user.id
    })

    res.json({ Like })
})

router.delete("/unlike/comments/:id", auth, async(req, res) => {
    const { id } = req.params;
    const user = res.locals.user;

    await prisma.commentLike.deleteMany({
        where: {
            commentId: Number(id),
            userId: Number(user.id)
        }
    })

    res.json({ msg: `Unlike comment ${id}` })
})

router.get("/likes/posts/:id", async(req, res) => {
    const { id } = req.params;

    const data = await prisma.postLike.findMany({
        where: {
            postId: Number(id)
        },
        include: {
            user: {
                include: {
                    followers: true,
                    following: true
                }
            }
        }
    })

    res.json(data)
})

router.get("/likes/comments/:id", async() => {
    const { id } = req.params;

    const data = await prisma.commentLike.findMany({
        where: {
            commentId: Number(id)
        },
        include: {
            user: {
                include: {
                    followers: true,
                    following: true
                }
            }
        }
    })
    res.json(data)
})

router.get("/following/posts", auth, async(req, res) => {
    const user = res.locals.user;

    const follow = await prisma.follow.findMany({
        where: {
            followerId: Number(user.id)
        }
    });

    const users = follow.map(item => item.followingId);

    const data = await prisma.post.findMany({
        where: {
            userId: { in: users
            }
        },
        include: {
            user: true,
            comments: true,
            Likes: true
        },
        orderBy: { id: "desc" },
        take: 20
    });
    res.json(data)
})

router.get("/friend/posts", auth, async(req, res) => {
    const user = res.locals.user;

    const friend = await prisma.friend.findMany({
        where: {
            friendId: Number(user.id)
        }
    })

    const friends = friend.map(item => item.friendId);

    const data = await prisma.post.findMany({
        where: {
            userId: { in: friends
            }
        },
        include: {
            user: true,
            comments: true,
            Likes: true
        },
        orderBy: { id: "desc" },
        take: 20
    });
    res.json(data)
})

router.get("/notis", auth, async(req) => {
    const user = res.locals.user;
    const notis = await prisma.noti.fin({
        where: {
            post: {
                userId: Number(user.id)
            },
        },
        include: { user: true },
        orderBy: { id: "desc" },
        take: 20
    });

    res.json(notis);
})

router.put("/notis/read", auth, async(req, res) => {
    const user = res.locals.user;

    await prisma.noti.updateMany({
        where: {
            post: {
                userId: Number(user.id),
            },
        },
        data: { read: true },
    });

    res.json({ msg: "Marked all notis read" })
})

router.put("/notis/read/:id", auth, async(req, res) => {
    const { id } = req.params;

    const noti = await prisma.noti.update({
        where: { id: Number(id) },
        data: { read: true }
    });

    res.json(noti)
})

async function addNoti({ type, content, postId, userId }) {
    const post = await prisma.post.findUnique({
        where: {
            id: Number(postId)
        },
    });

    if (post.userId == userId) return false;

    clients.map(client => {
        if (client.userId == post.userId) {
            client.ws.send(JSON.stringify({ event: "noti" }));
            console.log(`WS: event sent to ${client.userId}: noti`)
        }
    })

    return await prisma.noti.create({
        data: {
            type,
            content,
            postId: Number(postId),
            userId: Number(userId)
        },
    });
}

export default router