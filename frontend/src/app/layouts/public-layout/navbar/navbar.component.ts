import { Component, ChangeDetectionStrategy, inject } from '@angular/core';

import {
  Router,
  RouterLink,
  RouterLinkActive
} from '@angular/router';

import { AuthService } from '../../../core/services/auth.service';



@Component({

  selector: 'app-navbar',

  standalone: true,

  imports: [

    RouterLink,

    RouterLinkActive

  ],

  templateUrl:

    './navbar.component.html',

  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrl:

    './navbar.component.css'

})
export class NavbarComponent {

  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  readonly currentUser = this.authService.currentUser;


  mobileMenuOpen = false;



  toggleMenu(): void {

    this.mobileMenuOpen =
      !this.mobileMenuOpen;

  }



  closeMenu(): void {

    this.mobileMenuOpen =
      false;

  }



  logout(): void {

    this.authService.logout();

    this.closeMenu();

    this.router.navigateByUrl('/');

  }


}