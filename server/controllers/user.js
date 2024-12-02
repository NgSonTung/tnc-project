const UserDAO = require("../DAO/UserDAO");
const DTOUser = require("../DTO/Default/DTOUser");
const authController = require("./auth");
const OrderDAO = require("../DAO/OrderDAO");
const AuthUltils = require("../Utils/AuthUtils");
exports.getUserById = async (req, res) => {
  const id = req.params.id * 1;
  try {
    const user = await UserDAO.getUserById(id);
    console.log("ok");
    if (!user) {
      return res
        .status(404) //NOT FOUND
        .json({
          Code: 404,
          Msg: `Not found user with Id ${id}!`,
        });
    }
    req.user = user;
    return res.status(200).json({
      Code: 200,
      Msg: null,
      Data: user,
    });
  } catch (e) {
    return res.status(500).json({
      Code: 500,
      Msg: e.toString(),
    });
  }
};

exports.getUsers = async (req, res) => {
  const users = await UserDAO.getAllUsers(req.query);
  res.status(200).json({
    Code: 200,
    Msg: "OK",
    Page: users.Page,
    PageSize: users.PageSize,
    TotalPage: users.TotalPage,
    TotalUser: users.TotalUser,
    DataUsers: users.DataUsers,
  });
};

// exports.getUser = async (req, res) => {
//   try {
//     const user = req.user;
//     res.status(200).json({
//       Code: 200,
//       Msg: "OK",
//       Data: { user },
//     });
//   } catch (e) {
//     console.error(e);
//     res
//       .status(500) // 500 - Internal Error
//       .json({
//         Code: 500,
//         Msg: e.toString(),
//       });
//   }
// };

exports.getUserByUserName = async (req, res) => {
  try {
    const username = req.params.username;
    const user = await UserDAO.getUserByUserName(username);
    if (!user) {
      return res
        .status(404) /// 404 - NOT FOUND!
        .json({
          Code: 404,
          Msg: `Not found user with name ${username}`,
        });
    }
    res.status(200).json({
      Code: 200,
      Msg: null,
      Data: user,
    });
  } catch (e) {
    console.error(e);
    return res
      .status(500) // 500 - Internal Error
      .json({
        Code: 500,
        Msg: e.toString(),
      });
  }
};

exports.addUser = async (req, res) => {
  const newUser = req.body;
  const dto = new DTOUser(newUser);
  try {
    const userAdded = await UserDAO.userSignUp(dto);
    res.status(200).json({
      Code: 200,
      Msg: "added",
      Data: userAdded,
    });
  } catch (Error) {
    res.status(404).json({
      Code: 404,
      Msg: Error.toString(),
    });
  }
};

exports.updateUserById = async (req, res) => {
  const id = req.params.id * 1;
  try {
    const updateInfo = req.body;
    let user = await UserDAO.getUserById(id);
    if (!user) {
      return res.status(404).json({
        Code: 404,
        Msg: `Not found user with Id ${id}!`,
      });
    }
    await UserDAO.updateUserById(id, updateInfo);
    user = await UserDAO.getUserById(id);
    return res.status(200).json({
      Code: 200,
      Msg: null,
      Data: user,
    });
  } catch (e) {
    console.log(e);
    res.status(500).json({
      Code: 500,
      Msg: `Update user with id: ${id} failed! ${e.toString()}`,
    });
  }
};

exports.deleteUserById = async (req, res) => {
  const id = req.params.id * 1;
  try {
    const user = await UserDAO.getUserById(id);
    if (!user) {
      return res
        .status(404) //NOT FOUND
        .json({
          Code: 404,
          Msg: `User with Id ${id} not found!`,
        });
    }
    const token = AuthUltils.getTokenFromReq(req);
    const payload = AuthUltils.verificationToken(token);
    if (payload.AuthID < user.AuthID) {
      await UserDAO.deleteUserById(id);
    } else {
      return res
        .status(403) //NOT FOUND
        .json({
          Code: 403,
          Msg: "You don't have permission to perform this action !!",
        });
    }

    return res.status(200).json({
      Code: 200,
      Msg: `Deleted user with id ${id} successfully!`,
    });
  } catch (e) {
    console.log(e);
    return res.status(500).json({
      Code: 500,
      Msg: e.toString(),
    });
  }
};

exports.deleteMultipleUserById = async (req, res) => {
  const idList = req.query.id;
  try {
    if (!idList || idList.length === 0) {
      return res.status(403).json({
        Code: 403,
        Msg: `Invalid ids`,
      });
    }
    const token = AuthUltils.getTokenFromReq(req);
    const payload = AuthUltils.verificationToken(token);
    // console.log(payload);
    await UserDAO.deleteMultipleUserById(idList, payload);
    return res.status(200).json({
      Code: 200,
      Msg: null,
    });
  } catch (e) {
    console.log(e);
    return res.status(500).json({
      Code: 500,
      Msg: `Delete users with id ${idList} failed! ${e.toString()}`,
    });
  }
};
exports.changePassword = async (req, res) => {
  try {
    const reqBody = req.body;
    await UserDAO.changePassword(reqBody);
    return res.status(200).json({
      Code: 200,
      Msg: null,
    });
  } catch (e) {
    return res.status(500).json({
      Code: 500,
      Msg: e.toString(),
    });
  }
};
