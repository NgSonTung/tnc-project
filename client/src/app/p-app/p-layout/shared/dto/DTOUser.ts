export class DTOUser {
  UserID: number;
  UserName: string;
  Password: string;
  AuthID: number;
  Email: string;
  Point: number;
  Address: string;
  Phone: string;
  FullName: string;
  CreateAt: string;

  constructor(
    userID: number,
    userName: string,
    password: string,
    authID: number,
    email: string,
    point: number,
    fullname: string,
    address: string,
    phone: string,
    createAt: string
  ) {
    this.UserID = userID;
    this.UserName = userName;
    this.Password = password;
    this.AuthID = authID;
    this.Email = email;
    this.Point = point;
    this.FullName = fullname;
    this.Address = address;
    this.Phone = phone;
    this.CreateAt = createAt;
  }
}
