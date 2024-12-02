import { Component } from '@angular/core';
import { AuthService } from '../p-app/http-interceptors/auth.service';
import { Subject, takeUntil } from 'rxjs';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Ps_UtilObjectService } from '../p-lib/ultilities/ulity.object';
import { Router } from '@angular/router';
import { FormValidatorModule, required } from '@popeyelab/ngx-validator';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormValidatorModule],
})
export class LoginComponent {
  ngUnsubscription$ = new Subject<void>();
  signUpForm: FormGroup = new FormGroup({
    UserName: new FormControl('', [required('Vui lòng nhập tài khoản')]),
    Password: new FormControl('', [required('Vui lòng nhập mật khẩu')])
  })


  constructor(private authService: AuthService, private route: Router) {}

  onSignUp() {
    if (!this.signUpForm.invalid) {
      const userLogin = {
        UserName: this.signUpForm.controls['UserName'].value,
        Password: this.signUpForm.controls['Password'].value,
      }
      this.authService.login(userLogin).pipe(takeUntil(this.ngUnsubscription$)).subscribe(res => {
        if (Ps_UtilObjectService.hasValue(res)) {
          this.route.navigate(['/admin']);
        }
      });
    }
  }
}
