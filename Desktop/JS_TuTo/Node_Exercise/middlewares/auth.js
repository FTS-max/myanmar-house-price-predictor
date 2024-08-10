import express from 'express'
import jwt from 'jsonwebtoken'
import prisma from "../prismaClient.js"


function auth(req, res, next) {
    const {authorization} = req.headers;
    const token = authorization && authorization.split(" ")[0];

    if(!token){
        return res.status(400).json({msg:"token requird"})
    }

    const user = jwt.decode(token, process.env.JWT_SECRET);

    if(!user){
        return res.status(401).json({msg:"incorrect token"});
    }

    res.locals.user = user

    next();
}

function isOwner(type){
    return async (req, res, next)=>{
        const {id} = req.params;
        const user = req.locals.user;

        if(type == "post"){
            const post = await prisma.post.findUnique({
                where:{id:Number(id)}
            });

            if(post.userId == user.id) return next();
        }

        if(type == "comment"){
            const comment = await prisma.comment.findUnique({
                where: {id:Number(id)},
                include:{
                    post:true,
                }
            });

            if(comment.userId == user.id || comment.post.userId == user.id) return next();

        };
        res.status(403).json({msg:"Unauthorizate to delete"});
    }
}

export default {auth, isOwner};