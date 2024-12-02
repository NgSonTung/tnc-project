export class DTOUser {
  AuthID: number;
  AuthName: string;
  CreateAt: string;

  constructor(authID: number, authName: string, createAt: string) {
    this.AuthID = authID;
    this.AuthName = authName;
    this.CreateAt = createAt;
  }
}
