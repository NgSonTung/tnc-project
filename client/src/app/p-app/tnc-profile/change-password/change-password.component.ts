import { AfterViewInit, Component, SkipSelf, ViewChild } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { TextBoxComponent } from '@progress/kendo-angular-inputs';
import { UserService } from '../../p-layout/shared/services/user.service';
import { StorageService } from '../../p-layout/shared/services/storage.service';
import { NotificationService } from '@progress/kendo-angular-notification';
import { NotificationPopupService } from '../../p-layout/shared/services/notification.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-change-password',
  templateUrl: './change-password.component.html',
  styleUrls: ['./change-password.component.scss'],
})
export class ChangePasswordComponent implements AfterViewInit {
  @ViewChild('password') private password: TextBoxComponent;
  @ViewChild('repeatPassword') private repeatPassword: TextBoxComponent;
  ngUnsubscribe = new Subject<void>();

  constructor(
    @SkipSelf() private userService: UserService,
    @SkipSelf() private storageService: StorageService,
    @SkipSelf() private notifyService: NotificationPopupService
  ) {}

  changePassWordForm: FormGroup = new FormGroup({
    PassWord: new FormControl(''),
    RepeatPassWord: new FormControl(''),
  });

  ngAfterViewInit(): void {
    this.password.input.nativeElement.type = 'password';
    this.repeatPassword.input.nativeElement.type = 'password';
  }

  updatePassword(): void {
    const oldPassword = this.changePassWordForm.get('PassWord').value;
    const newPassword = this.changePassWordForm.get('RepeatPassWord').value;
    const userID = this.storageService.getUser().UserID;
    const user = {
      OldPassword: oldPassword,
      NewPassword: newPassword,
      UserID: userID,
    };

    this.userService
      .changePasword(user)
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe((res) => {
        console.log(res);

        if (res.Code == 200) {
          window.location.reload();
          this.notifyService.onSuccess('Đổi mật khẩu thành công!');
        }
      });
  }

  public toggleVisibility(type: string): void {
    if (type === 'password') {
      const inputEl = this.password.input.nativeElement;
      inputEl.type = inputEl.type === 'password' ? 'text' : 'password';
    } else {
      const inputEl = this.repeatPassword.input.nativeElement;
      inputEl.type = inputEl.type === 'password' ? 'text' : 'password';
    }
  }
}
