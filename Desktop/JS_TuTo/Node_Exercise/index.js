import express from 'express'
import expressWs from 'express-ws'
import cors from 'cors'
import prisma from './prismaClient.js'
import contentRouter from './router/content.js'
import userRouter from './router/user.js';
import { wsRouter } from "./router/ws.js"

const app = express()
expressWs(app)
app.use(express.json());
app.use(cors())
app.use('/content', contentRouter)
app.use('/', userRouter)
app.use("/", wsRouter)

app.listen(8000, (req, res) => {
    console.log("Your API is listening at port 8000")
})

const gracefulShutdown = async() => {
    await prisma.$disconnect();
    server.close(() => {
        console.log("Your API is closed")
        process.exit(0);
    })
}

process.on("SIGTERM", gracefulShutdown)
process.on("SIGINT", gracefulShutdown)