import { PrismaClient } from "@prisma/client";
import { faker } from "@faker-js/faker"

const prisma = new PrismaClient();
async function CommentSeeder() {
    const data = [];

    for (let i = 0; i < 40; i++) {
        const content = faker.lorem.paragraph();
        const userId = faker.number.int({ min: 1, max: 10 })
        const postId = faker.number.int({ min: 1, max: 20 })

        data.push({ content, userId, postId })
    }

    console.log("Post seeding started...")
    await prisma.comment.createMany({ data })
    console.log("Post seeding Done...")
}

export default CommentSeeder