import { Routes } from '@angular/router';

import { PublicLayoutComponent } from './layouts/public-layout/public-layout.component';
import { adminGuard } from './core/guards/admin.guard';


export const routes: Routes = [


  {
    path: '',

    component: PublicLayoutComponent,

    children: [

      {
        path: '',

        loadComponent: () =>
          import('./pages/home/home.component')
            .then(m => m.HomeComponent)

      },
      {
        path:'services/:slug',
        
        loadComponent:()=> 
        import('./pages/service-detail/service-detail.component')
        .then(m=>m.ServiceDetailComponent)
        
        },

      {
        path: 'about',

        loadComponent: () =>
          import('./pages/about/about.component')
            .then(m => m.AboutComponent)

      },


      {
        path: 'services',

        loadComponent: () =>
          import('./pages/services/services.component')
            .then(m => m.ServicesComponent)

      },


      {
        path: 'gallery',

        loadComponent: () =>
          import('./pages/gallery/gallery.component')
            .then(m => m.GalleryComponent)

      },


      {
        path: 'resources',

        loadComponent: () =>
          import('./pages/resources/resources.component')
            .then(m => m.ResourcesComponent)

      },


      {
        path: 'blog',

        loadComponent: () =>
          import('./pages/blog/blog.component')
            .then(m => m.BlogComponent)

      },


      {
        path: 'blog/:slug',

        loadComponent: () =>
          import('./pages/blog/blog-post-detail/blog-post-detail.component')
            .then(m => m.BlogPostDetailComponent)

      },


      {
        path: 'contact',

        loadComponent: () =>
          import('./pages/contact/contact.component')
            .then(m => m.ContactComponent)

      },


      {
        path: 'login',

        loadComponent: () =>
          import('./pages/login/login.component')
            .then(m => m.LoginComponent)

      },


      {
        path: 'register',

        loadComponent: () =>
          import('./pages/register/register.component')
            .then(m => m.RegisterComponent)

      },


      {
        path: 'admin',

        canActivate: [adminGuard],

        loadComponent: () =>
          import('./pages/admin/admin.component')
            .then(m => m.AdminComponent)

      },


      {
        path: 'admin/blog',

        canActivate: [adminGuard],

        loadComponent: () =>
          import('./pages/admin-blog/admin-blog.component')
            .then(m => m.AdminBlogComponent)

      },


      {
        path: 'admin/blog/new',

        canActivate: [adminGuard],

        loadComponent: () =>
          import('./pages/admin-blog/post-editor/post-editor.component')
            .then(m => m.PostEditorComponent)

      },


      {
        path: 'admin/blog/:slug/edit',

        canActivate: [adminGuard],

        loadComponent: () =>
          import('./pages/admin-blog/post-editor/post-editor.component')
            .then(m => m.PostEditorComponent)

      },


      {
        path: 'privacy-policy',

        loadComponent: () =>
          import('./pages/privacy-policy/privacy-policy.component')
            .then(m => m.PrivacyPolicyComponent)

      },


      {
        path: 'terms',

        loadComponent: () =>
          import('./pages/terms/terms.component')
            .then(m => m.TermsComponent)

      },
      {
        path: '**',
        loadComponent: () =>
        import('./pages/not-found/not-found.component')
        .then(
        component => component.NotFoundComponent
        )
       }
    ]

  },


  {
    path: '**',

    redirectTo: ''

  }


];