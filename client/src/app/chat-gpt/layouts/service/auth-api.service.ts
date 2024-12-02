import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root',
})
export class AuthApiService {
  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable<any> {
    const body = {
      userName: username,
      password: password,
    };

    return this.http
      .post('/api/v1/auth/login', body)
      .pipe(catchError(this.handleError));
  }

  register(username: string, password: string, email: string): Observable<any> {
    const body = {
      userName: username,
      password: password,
      email: email,
    };

    return this.http
      .post('/api/v1/auth/register', body)
      .pipe(catchError(this.handleError));
  }

  private handleError(e: any) {
    return throwError(() => new Error(e.error.message));
  }
}
