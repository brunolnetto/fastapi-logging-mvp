<template>
  <div id="app">
    <nav>
      <router-link to="/">Dashboard</router-link>
      <router-link to="/tasks">Tasks</router-link>
    </nav>
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
};
</script>

<style>
nav {
  padding: 1em;
  background-color: #282c34;
}

nav a {
  margin: 0 15px;
  color: #61dafb;
  text-decoration: none;
}
</style>
