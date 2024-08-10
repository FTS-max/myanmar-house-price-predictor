import { PrismaClient } from '@prisma/client'
import { faker } from '@faker-js/faker'
import bcrypt from 'bcrypt'

const prisma = new PrismaClient()

async function UserSeeder() {
    const password = await bcrypt.hash("password", 10)
    console.log("User seeding started...")

    for (let i = 0; i < 10; i++) {
        const firstName = faker.person.firstName();
        const LastName = faker.person.lastName();

        const name = `${firstName} ${LastName}`;
        const username = `${firstName}${LastName[0]}`.toLocaleLowerCase();
        const bio = faker.person.bio()

        await prisma.user.upsert({
            where: { username },
            update: {},
            create: { name, username, bio, password }
        });

        console.log("User seeder is done...")
    }
}
export default UserSeeder