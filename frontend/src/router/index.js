import Vue from 'vue'
import Router from 'vue-router'
Vue.use(Router)

export default new Router({
  routes: [
    {
    path: '/',
    name: 'index',
    // component: main, 
    component: ()=> import('@/pages/main')
  },
  {
    path: '/rec',
    name: 'rec',
    component: ()=> import('@/pages/rec'),
    // children: [
    //   {
    //     path: '/rec/questions',
    //     components: {second: ()=> import('@/components/questions')}
    //   }
    // ]
  },
  {
    path: '/query',
    name: 'query',
    component: ()=> import('@/pages/query')
  },
  {
    path: '/guide',
    name: 'guide',
    component: () => import('@/pages/guide')
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('@/pages/about')
  }

  ]
})
