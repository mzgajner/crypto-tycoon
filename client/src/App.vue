<template>
    <div>
        <button @click="startBuilding">
            Build house
        </button>
        <h1>money: {{ money }}</h1>
        <div id="app" v-if="grid.length>0" :class="wrapperClass">
            <div class="row" v-for="(row, row_index) in grid">
                <div
                    v-for="(column, column_index) in row"
                    :class="'column ' + column.type"
                    @click="build(column, row_index, column_index)"
                >
                    <template v-for="object in column.content">
                        <div v-if="object.type === 'person'" class="person"></div>
                        <div v-else-if="object.type === 'house'" class="house"></div>
                    </template>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import io from 'socket.io-client'

let server = io.connect('http://localhost:5000');


export default {
    name: 'app',
    data () {
        return {
            grid: [],
            building: false,
            money: 0,
            id: null,
        }
    },
    computed: {
        wrapperClass() {
            return this.building ? 'is-building' : '';
        },
        cellsWithContent() {
            let cellsWithContents = [];
            this.grid.forEach(row => {
                row.forEach(column => {
                    if(column.content) {
                        cellsWithContents.push(column);
                    }
                })
            })
            return cellsWithContents;
        }
    },
    methods: {
        startBuilding() {
            this.building = true;
        },
        build(column, x, y) {
            if (column.type !== 'land') return;
            this.building = false;
            let bla = io.connect('http://localhost:5000');
            bla.emit('build', {
                position: [x, y],
                money: this.money,
                player_id: this.id
            });
        }
    },
    created() {
        this.id = Math.floor(Math.random() * 64);
        server.emit('register',{ id: this.id });
        server.on('update', (payload) => {
            console.log('start occured', payload);
            this.grid = payload.world;
            this.money = payload.money[this.id];
        });
    },
}
</script>

<style lang="scss">
    .row {
        display:flex;
    }
    .column {
        width:40px;
        height:40px;
        position: relative;
        &.land {
            background-color: green;
        }
        &.road {
            background-color: grey;
        }
    }

    .is-building {
        .land:hover {
            background-color: greenyellow;
        }
    }

    .person {
        left: 10px;
        top: 10px;
        border-radius: 50px;
        height: 20px;
        width: 20px;
        background-color: black;
        position: absolute;
    }
</style>
