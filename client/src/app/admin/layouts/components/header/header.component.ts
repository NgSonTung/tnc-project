import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { AuthService } from 'src/app/p-app/http-interceptors/auth.service';
import { StorageService } from 'src/app/p-app/p-layout/shared/services/storage.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss'],
})
export class HeaderComponent {
  currentUserName: string;
  private unsubscription = new Subject<void>();

  constructor(
    private storageService: StorageService, 
    private authService: AuthService, 
    private router: Router
  ) {}

  ngOnInit(): void {
    this.currentUserName = this.storageService.getUser().UserName;
    console.log(this.currentUserName);
  }

  logOut() {
    this.authService
        .logout()
        .pipe(takeUntil(this.unsubscription))
        .subscribe((res) => {
          console.log(res);
        });
      this.storageService.clean();
      this.router.navigateByUrl('/login');
  }

  user = { userName: 'Alex', avatar: 'assets/icon/cat.jpg' };
}
