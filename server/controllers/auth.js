const jwt = require("jsonwebtoken");
const UserDAO = require("../DAO/UserDAO");
const AuthDAO = require("../DAO/AuthDAO");
const DTOUser = require("../DTO/Default/DTOUser");
const utils = require("../Utils/AuthUtils");
exports.login = async (req, res) => {
  let code;
  const form = req.body;
  try {
    if (form.Code) {
      code = form.Code;
      delete form.Code;
    }
    const dto = new DTOUser(form);
    const result = await utils.login(dto);
    res.cookie("user", result.Token, {
      httpOnly: true,
    });
    //test
    res.cookie("ruser", result.RefreshToken, {
      httpOnly: true,
    });
    res.cookie("csrf-token", result.CsrfToken, {});
    if (code === 1) {
      res.status(200).json({
        Code: 200,
        Msg: "OK, Sign Up & Login Success !!",
        Data: result,
      });
    } else {
      res.status(200).json({
        Code: 200,
        Msg: "OK",
        Data: result,
      });
    }
  } catch (e) {
    console.log(e);

    if (code === 1) {
      res.status(401).json({
        Code: 401,
        Msg: `Fail, Sign Up & Login Fail !!${e.toString()}`,
      });
    } else {
      res.status(401).json({
        Code: 401,
        Msg: `Fail ${e.toString()}`,
      });
    }
  }
};

exports.logout = async (req, res) => {
  try {
    const cookieKeys = Object.keys(req.cookies);
    for (let i = 0; i < cookieKeys.length; i++) {
      res.clearCookie(cookieKeys[i]);
    }
    //delete rtoken and token here
    const result = await utils.logout(req);
    if (result) {
      return res.status(200).json({
        Code: 200,
        Msg: "log out !!",
      });
    } else {
      throw new Error("Logout failed !!");
    }
  } catch (err) {
    res.status(404).json({
      Code: 404,
      Msg: err.toString(),
    });
  }
};

exports.signup = async (req, res) => {
  try {
    const form = req.body;
    if (!form.Password || !form.UserName || !form.Email) {
      return res.status(403).json({
        Code: 403,
        Msg: `Invalid Password`,
      });
    }
    const dto = new DTOUser(form);
    const user = await UserDAO.userSignUp(dto);
    delete user.Password;
    delete user.AuthID;
    // console.log("usertest", user);
    req.body = {
      Code: 1,
      UserName: form.UserName,
      Password: form.Password,
    };
    this.login(req, res);
  } catch (e) {
    console.log(e);

    if (e) {
      return res.status(403).json({
        Code: 403,
        Msg: e.toString(),
      });
    }
  }
};

exports.protect = async (req, res, next) => {
  try {
    const newToken = await utils.protect(req);
    if (!newToken.currentUser) {
      req.user = newToken;
    } else {
      req.user = newToken.User;
    }
    req.cookies.user = newToken.Token || req.cookies.user;
    req.cookies.RefreshToken = newToken.RefreshToken || req.cookies.ruser;
    res.cookie("user", newToken.Token || req.cookies.user, {
      httpOnly: true,
    });
    res.cookie("ruser", newToken.RefreshToken || req.cookies.ruser, {
      httpOnly: true,
    });
    res.cookie("csrf-token", newToken.CSRFToken || req.cookies["csrf-token"]);
  } catch (e) {
    console.log(e);

    return res
      .status(500) // 500 - Internal Error
      .json({
        Code: 500,
        Msg: e.toString(),
      });
  }
  next();
};

//roles
exports.restrictTo = (roles) => {
  return async (req, res, next) => {
    if (utils.checkRole(req, roles)) {
      next();
    } else {
      return res
        .status(403) // 403 - Forbidden
        .json({
          Code: 403,
          Msg: "You do not have permission to perform this action",
        });
    }
  };
};

exports.getTokenDev = async (req, res) => {
  try {
    const master = {
      UserName: "master",
      Password: "1",
    };

    const result = await utils.login(master);
    delete result.User;
    res.cookie("user", result.Token, {
      httpOnly: true,
    });
    res.cookie("ruser", result.RefreshToken, {
      httpOnly: true,
    });
    res.cookie("csrf-token", result.CsrfToken, {});

    res.status(200).json({
      Code: 200,
      Msg: "OK",
      Data: result,
    });
  } catch (e) {
    console.log(e);

    res
      .status(500) // 500 - Internal Error
      .json({
        Code: 500,
        Msg: e.toString(),
      });
  }
};

exports.getRefreshToken = async (req, res) => {
  try {
    const rToken = req.body || req.headers || req.cookies;
    const newRToken = await utils.handleRefreshToken(rToken);
    res.status(200).json({
      Code: 200,
      Msg: "OK",
      Data: newRToken,
    });
  } catch (e) {
    console.log(e);

    res
      .status(500) // 500 - Internal Error
      .json({
        Code: 500,
        Msg: e.toString(),
      });
  }
};

exports.cleanRToken = async (req, res) => {
  try {
    const result = await AuthDAO.cleanRToken();
    res.status(200).json({
      Code: 200,
      Msg: "OK",
      Data: result,
    });
  } catch (e) {
    console.log(e);

    res
      .status(500) // 500 - Internal Error
      .json({
        Code: 500,
        Msg: e.toString(),
      });
  }
};
