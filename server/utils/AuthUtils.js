const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");
const {v4: uuidv4, v5: uuidv5, NIL: uuidNil} = require("uuid");

const OrderDAO = require("../DAO/OrderDAO");
const UserDAO = require("../DAO/UserDAO");
const AuthDAO = require("../DAO/AuthDAO");
const DateTimeUtils = require("./DateTimeUtils");
const signToken = (id, username, authID, OrderID = []) => {
  return jwt.sign(
    {
      UserID: id,
      Username: username,
      AuthID: authID,
      OrderID: OrderID,
    },
    process.env.JWT_SECRET,
    {expiresIn: process.env.JWT_EXPIRED_IN}
  );
};

const signRToken = (
  id,
  username,
  authID,
  OrderID = [],
  expiresIn = process.env.REFRESH_JWT_EXPRIRED_IN
) => {
  return jwt.sign(
    {
      UserID: id,
      Username: username,
      AuthID: authID,
      OrderID: OrderID,
    },
    process.env.REFRESH_JWT_SECRET,
    {expiresIn: expiresIn}
  );
};

const validateRefreshToken = async (userID = null, refreshToken) => {
  let oldUserRFT;
  if (userID !== null) {
    oldUserRFT = await AuthDAO.getRefreshTokenByUserID(userID);
  } else {
    oldUserRFT = await AuthDAO.getRefreshTokenByRefreshToken(refreshToken);
  }
  if (
    oldUserRFT &&
    oldUserRFT.RefreshToken &&
    DateTimeUtils.calculateTimeDifference(
      new Date().toISOString(),
      oldUserRFT.Expires,
      true
    ) &&
    oldUserRFT.RefreshToken === refreshToken
  ) {
    return true;
  }
  return false;
};

const createCSRFToken = () => uuidv4();

const protectCSRF = (req) => {
  const csrfToken = req.headers["csrf-token"];
  const csrfCookie = req.cookies["csrf-token"];
  if (csrfToken !== csrfCookie || !csrfToken || !csrfCookie) {
    return false;
  }
  return true;
};

/**
 * handle verify token
 **/
exports.verificationToken = (token, jwtSecret) => jwt.verify(token, jwtSecret);

/**
 * handle get new refresh token and new token
 */
exports.handleRefreshToken = async (refreshToken) => {
  try {
    const user = this.verificationToken(
      refreshToken.RefreshToken,
      process.env.REFRESH_JWT_SECRET
    );
    //const orderIDQuery = await OrderDAO.getOrderIDByUserName(user.UserName);

    if (validateRefreshToken(user.UserID, refreshToken.RefreshToken)) {
      const newUserToken = signToken(
        user.UserID,
        user.UserName,
        user.AuthID,
        user.OrderID
      );
      const newUserRFT = signRToken(
        user.UserID,
        user.UserName,
        user.AuthID,
        user.OrderID
      );
      const rRokenExpiresIn = DateTimeUtils.convertMillisecondsToDateTimeSQL(
        user.exp,
        1000
      );
      await AuthDAO.updateRefreshTokenByUserId(user.UserID, {
        RefreshToken: newUserRFT,
        Expires: rRokenExpiresIn,
      });
      user.exp && delete user.exp;
      user.iat && delete user.iat;
      const csrfToken = createCSRFToken();
      return {
        User: user,
        Token: newUserToken,
        RefreshToken: newUserRFT,
        CSRFToken: csrfToken,
      };
    } else {
      throw new Error("Invalid Token");
    }
  } catch (e) {
    throw new Error("Invalid Token");
  }
};

exports.getTokenFromReq = (req) => {
  let token;
  if (
    req.headers.authorization &&
    req.headers.authorization.startsWith("Bearer")
  ) {
    token = req.headers.authorization.split(" ")[1];
  } else {
    token = req.cookies.access_token_dev || req.cookies.user;
  }
  return token;
};

exports.getRefreshTokenFromReq = (req) => {
  let rToken;
  if (
    req.headers.authorization &&
    req.headers.authorization.startsWith("BearerRefreshToken")
  ) {
    rToken = req.headers.authorization.split(" ")[1];
  } else {
    rToken =
      req.body.ruser ||
      req.body.RefreshToken ||
      req.cookies.ruser ||
      req.query.ruser;
  }
  return rToken;
};

/**
 * Validate User and Return Token and Refresh Token
 */
exports.login = async (dto) => {
  //1. check if dto is valid
  if (!dto.Password || !dto.UserName) {
    throw new Error({Code: 403, Msg: `Invalid params`});
  }
  //2. check if user existed
  const user = await UserDAO.getUserByUserName(dto.UserName);
  const orderIDQuery = await OrderDAO.getOrderIDByUserName(dto.UserName);
  let orderID;
  if (!orderIDQuery) {
    orderID = -1;
  } else {
    orderID = orderIDQuery;
  }
  if (!user) {
    throw new Error({Code: 401, Msg: `Invalid user - ${dto.UserName}`});
  }
  //3. check if password is valid
  const isValidPassword = await bcrypt.compare(dto.Password, user.Password);
  if (!isValidPassword) {
    throw new Error({Code: 401, Msg: "Invalid authentication"});
  }
  //4. get JWT & response to use  //https://jwt.io/
  let token = signToken(user.UserID, user.UserName, user.AuthID, orderID);
  let rRoken = signRToken(user.UserID, user.UserName, user.AuthID, orderID);
  const expirationTime = this.verificationToken(
    rRoken,
    process.env.REFRESH_JWT_SECRET
  ).exp;
  const rRokenExpiresIn = DateTimeUtils.convertMillisecondsToDateTimeSQL(
    expirationTime,
    true
  );
  //res jwt cookie
  delete user.Password;
  const csrfToken = createCSRFToken();
  await AuthDAO.updateRefreshTokenByUserId(user.UserID, {
    RefreshToken: rRoken,
    Expires: rRokenExpiresIn,
  });
  return {
    Token: token,
    User: user,
    RefreshToken: rRoken,
    CsrfToken: csrfToken,
  };
};

exports.protect = async (req) => {
  let token = this.getTokenFromReq(req);
  let refreshToken = this.getRefreshTokenFromReq(req);
  let payload;
  let payloadRefresh;
  let msgXSRF = "";
  const pCSRF = protectCSRF(req);

  if (typeof refreshToken == "object") {
    refreshToken = refreshToken.RefreshToken;
  }
  // what will happend if refresh token is expired ?

  if (refreshToken) {
    try {
      payloadRefresh = this.verificationToken(
        refreshToken,
        process.env.REFRESH_JWT_SECRET
      );
    } catch (e) {
      await AuthDAO.deleteRefreshTokenByRefreshToken(refreshToken);
      throw new Error(`Invalid Refresh Token`);
    }
  }

  try {
    if (!token) {
      throw new Error("You are not logged in! Please log in to get access.");
    }
    if (!pCSRF) {
      msgXSRF = "CSRF Token";
      // throw new Error(`Invalid authentication ${msgXSRF}`);
      //...
    }
    payload = this.verificationToken(token, process.env.JWT_SECRET);
    const currentUser = await UserDAO.getUserById(payload.UserID);
    if (
      !currentUser ||
      !(await validateRefreshToken(currentUser.UserID, refreshToken))
    ) {
      throw new Error(`Invalid authentication`);
    }
    // console.log(currentUser);
    return currentUser;
  } catch (e) {
    if (
      (await validateRefreshToken(null, refreshToken)) &&
      token &&
      !payload &&
      pCSRF
    ) {
      const newToken = await this.handleRefreshToken({
        RefreshToken: refreshToken,
      });
      return newToken;
    } else {
      throw new Error(`Invalid authentication ${msgXSRF}`);
    }
  }
};

exports.checkRole = (req, roles) => {
  const roleUser = req.user.AuthID;
  if (
    (roleUser == 1 && roles == 2) ||
    ((roleUser == 1 || roleUser == 2) && roles == 3)
  ) {
    return true;
  }
  if (roles == roleUser) {
    return true;
  }
  return false;
  // switch (roleUser) {
  //   case roles.admin:
  //   case roles.master:
  //     return true;
  //   default:
  //     return false;
  // }
};

exports.logout = async (req) => {
  let refreshToken = this.getRefreshTokenFromReq(req);
  if (typeof refreshToken == "object") {
    refreshToken = refreshToken.RefreshToken;
  }
  if (!refreshToken) {
    throw new Error("You was logged out !!!");
  }
  if (await validateRefreshToken(null, refreshToken)) {
    await AuthDAO.deleteRefreshTokenByRefreshToken(refreshToken);
    return true;
  }
  return false;
};
