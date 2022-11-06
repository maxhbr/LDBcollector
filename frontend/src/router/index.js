import Vue from 'vue'
import Router from 'vue-router'
Vue.use(Router)

export default new Router({
  routes: [
    {
    path: '/',
    name: 'index',
    // component: main, 
    components : {first: ()=> import('@/pages/main')}
  },
  {
    path: '/rec',
    name: 'rec',
    components : {first: ()=> import('@/pages/rec')},
    children: [
      {
        path: '/rec/questions',
        components: {second: ()=> import('@/components/questions')}
      }
    ]
  },
  {
    path: '/query',
    name: 'query',
    components: {first: ()=> import('@/pages/query')}
  }
  ]
})
