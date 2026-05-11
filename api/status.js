const express = require("express");
const cors = require("cors");
const jwt = require("jsonwebtoken");
const cookieParser = require("cookie-parser");

const app = express();

app.set("trust proxy", 1);

const PORT = process.env.PORT || 3000;

const SECRET = process.env.JWT_SECRET || "PROJECT_CIRCUS_SECRET";

// ===== MIDDLEWARE =====

app.use(express.json());

app.use(cookieParser());

app.use(cors({
    origin: [
        "https://projectcircus.ru",
        "https://www.projectcircus.ru",
        "https://project-circus.vercel.app"
    ],
    credentials: true
}));

// ===== ТВОЯ БАЗА =====
// тут пример

const users = [
    {
        username: "admin",
        password: "123456",
        role: "admin",
        balance: 99999,
        realname: "Admin"
    },
    {
        username: "player",
        password: "123456",
        role: "player",
        balance: 500,
        realname: "Player"
    }
];

// ===== AUTH MIDDLEWARE =====

function auth(req, res, next){

    const token = req.cookies.token;

    if(!token){
        return res.status(401).json({
            status: "error",
            message: "Не авторизован"
        });
    }

    try{

        const decoded = jwt.verify(token, SECRET);

        req.user = decoded;

        next();

    }catch(err){

        return res.status(401).json({
            status: "error",
            message: "Неверный токен"
        });
    }
}

// ===== LOGIN =====

app.post("/login", async(req, res)=>{

    const { username, password } = req.body;

    const user = users.find(
        u => u.username.toLowerCase() === username.toLowerCase()
    );

    if(!user){

        return res.json({
            status: "error",
            message: "Игрок не найден"
        });
    }

    // тут потом можно bcrypt
    if(user.password !== password){

        return res.json({
            status: "error",
            message: "Неверный пароль"
        });
    }

    // JWT
    const token = jwt.sign({

        username: user.username,
        role: user.role

    }, SECRET, {

        expiresIn: "7d"
    });

    // COOKIE
    res.cookie("token", token, {

        httpOnly: true,

        secure: true,

        sameSite: "none",

        maxAge: 1000 * 60 * 60 * 24 * 7
    });

    res.json({
        status: "ok",
        username: user.username
    });
});

// ===== ME =====

app.get("/me", auth, (req, res)=>{

    res.json({
        status: "ok",
        username: req.user.username,
        role: req.user.role
    });
});

// ===== PROFILE =====

app.get("/profile", auth, (req, res)=>{

    const user = users.find(
        u => u.username === req.user.username
    );

    if(!user){

        return res.status(404).json({
            status: "error"
        });
    }

    res.json({

        status: "ok",

        realname: user.realname,

        role: user.role,

        balance: user.balance
    });
});

// ===== LOGOUT =====

app.post("/logout", (req, res)=>{

    res.clearCookie("token", {

        httpOnly: true,

        secure: true,

        sameSite: "none"
    });

    res.json({
        status: "ok"
    });
});

// ===== START =====

app.listen(PORT, ()=>{

    console.log("Server started on port " + PORT);

});
