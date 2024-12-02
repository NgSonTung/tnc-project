import { Component, OnInit, SkipSelf } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { StorageService } from '../../p-layout/shared/services/storage.service';
import { DTOUser } from '../../p-layout/shared/dto/DTOUser';
import { UserService } from '../../p-layout/shared/services/user.service';

@Component({
  selector: 'app-personal-info',
  templateUrl: './personal-info.component.html',
  styleUrls: ['./personal-info.component.scss'],
})
export class PersonalInfoComponent implements OnInit {
  personalForm: FormGroup;
  userInfo: DTOUser;
  constructor(
    @SkipSelf() private userService: UserService,
    private storageService: StorageService
  ) {}

  ngOnInit(): void {
    this.loadPersonalForm();
    const userInfo = this.storageService.getUser();
    this.userInfo = userInfo;
    this.personalForm.patchValue(userInfo);
  }

  // convenience getter for easy access to form fields
  get f() {
    return this.personalForm.controls;
  }

  updateUserInfo() {
    const user = {
      UserName: this.personalForm.get('UserName').value,
      FullName: this.personalForm.get('FullName').value,
      Email: this.personalForm.get('Email').value,
      Phone: this.personalForm.get('Phone').value,
      Address: this.personalForm.get('Address').value,
    };

    this.userService.updateData(this.userInfo.UserID, user).subscribe((res) => {
      this.storageService.saveUser(res.Data);
      window.location.reload();
    });
  }

  loadPersonalForm() {
    this.personalForm = new FormGroup({
      UserName: new FormControl(''),
      FullName: new FormControl(''),
      Email: new FormControl('', Validators.email),
      TotalPrice: new FormControl(''),
      Address: new FormControl(''),
      Phone: new FormControl(''),
    });
  }
}
