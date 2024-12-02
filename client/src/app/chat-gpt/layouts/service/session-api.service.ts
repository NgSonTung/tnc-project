import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root',
})
export class SessionApiService {
  constructor(private http: HttpClient) {}

  getSessions(): Observable<any> {
    return this.http.get('/api/v1/session').pipe(catchError(this.handleError));
  }

  getSessionById(id: string): Observable<any> {
    return this.http.get('api/v1/chatbot/1').pipe(catchError(this.handleError));
  }

  private handleError(e: any) {
    return throwError(() => new Error(e.error.message));
  }
}
