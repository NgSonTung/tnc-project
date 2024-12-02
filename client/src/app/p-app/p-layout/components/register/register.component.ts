import { Component, Input, OnInit, SkipSelf } from '@angular/core';
import { RegisterService } from '../../shared/services/register.service';
import {
  FormControl,
  FormGroup,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { confirmPassword } from '../../shared/directives/registerationForm.directive';
import { AuthService } from 'src/app/p-app/http-interceptors/auth.service';
import { Subject, takeUntil } from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';
import { StorageService } from '../../shared/services/storage.service';
import { NotificationPopupService } from '../../shared/services/notification.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss'],
})
export class RegisterComponent implements OnInit {
  submitted = false;
  isRegister: boolean = false;
  returnUrl: string = '';
  ngUnsubscribe = new Subject<void>();
  loginForm: FormGroup = new FormGroup({
    UserName: new FormControl('', Validators.required),
    Password: new FormControl('', Validators.required),
  });

  registerForm: FormGroup = new FormGroup(
    {
      UserName: new FormControl('', Validators.required),
      Password: new FormControl('', Validators.required),
      ConfirmPassword: new FormControl(null, Validators.required),
      Email: new FormControl(null, Validators.required),
    },
    { validators: confirmPassword }
  );

  constructor(
    @SkipSelf() private registerService: RegisterService,
    private authService: AuthService,
    private route: ActivatedRoute,
    private router: Router,
    private storageService: StorageService,
    private notificationService: NotificationPopupService
  ) {
    // redirect to home if already logged in
    if (this.authService.currentUserValue) {
      this.router.navigate(['/']);
    }
  }

  ngOnInit(): void {
    // get return url from route parameters or default to '/'
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/';
  }

  get _loginForm() {
    return this.loginForm.controls;
  }

  get _registerForm() {
    return this.registerForm.controls;
  }

  toggleShowRegister(): void {
    this.registerService.toggleRegisterShown();
  }

  toggleRegister(): void {
    this.isRegister = !this.isRegister;
  }

  // getFormValidationErrors() {
  //   Object.keys(this.registerForm.controls).forEach((key) => {
  //     const controlErrors: ValidationErrors = this.registerForm.get(key).errors;
  //     if (controlErrors != null) {
  //       Object.keys(controlErrors).forEach((keyError) => {
  //         console.log(
  //           'Key control: ' + key + ', keyError: ' + keyError + ', err value: ',
  //           controlErrors[keyError]
  //         );
  //       });
  //     }
  //   });
  // }

  onSubmit(e: any): void {
    e.preventDefault();
    this.submitted = true;
    // this.getFormValidationErrors();

    if (this.isRegister) {
      const registerInfo = this.registerForm.value;
      this.authService
        .signUp(registerInfo)
        .pipe(takeUntil(this.ngUnsubscribe))
        .subscribe((res) => {
          console.log('CCCCCCCCCCCCCCCCC', res);

          if (res.Code === 200) {
            this.registerService.closeRegisterForm();
            this.notificationService.onSuccess('Đăng ký thành công');
            this.reloadPage();
          } else {
            this.notificationService.onError('Đăng ký thất bại');
          }
        });
    } else if (!this.isRegister) {
      this.authService
        .login(this.loginForm.value)
        .pipe(takeUntil(this.ngUnsubscribe))
        .subscribe((data) => {
          console.log('CCCCCCCCCCCCCCCCC', data);

          if (data.Code === 200) {
            this.registerService.closeRegisterForm();
            this.notificationService.onSuccess('Đăng nhập thành công');
            this.reloadPage();
          } else {
            this.notificationService.onError('Đăng nhập thất bại');
          }
        });
    }
  }

  reloadPage(): void {
    window.location.reload();
  }
}
