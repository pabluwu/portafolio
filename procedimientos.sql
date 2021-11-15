create or replace procedure sp_listar_tareas_departamento_realizadas(
    v_id_departamento number,
    v_realizado number,
    tareas out SYS_REFCURSOR
)
is

begin

    open tareas for select pt.id, pt.nombre, pt.descripcion, pt.realizado, pt.fechacreacion, pt.fechalimite, pt.fechatermino, pt.usuario_id from process_tarea pt
                        join process_user pu on pu.id=pt.usuario_id
                        where pu.departamento_id = v_id_departamento and pt.realizado = v_realizado;




end;


create or replace procedure sp_listar_tareas_departamento_total(
    v_id_departamento number,
    tareas out SYS_REFCURSOR
)
is

begin

    open tareas for select pt.id, pt.nombre, pt.descripcion, pt.realizado, pt.fechacreacion, pt.fechalimite, pt.fechatermino, pt.usuario_id, pu.username, ps.estadosemaforo from process_tarea pt
                        join process_user pu on pu.id=pt.usuario_id
                        join process_calculoestado pc on pc.id = pt.id
                        join process_semaforo ps on ps.calculoestado_id = pc.id
                        where pu.departamento_id = v_id_departamento
                        order by pt.realizado;

end;

create or replace procedure sp_listar_estado_tareas(
    v_id_departamento number,
    v_realizado number,
    v_estado varchar,
    tareas out SYS_REFCURSOR
)
is

begin

    open tareas for select pt.id, pt.nombre, pt.descripcion, pt.realizado, pt.fechacreacion, pt.fechalimite, pt.fechatermino, pt.usuario_id from process_tarea pt
                        join process_user pu on pu.id=pt.usuario_id
                        join process_calculoestado pc on pc.id = pt.id
                        join process_semaforo ps on ps.calculoestado_id = pc.id
                        where pu.departamento_id = v_id_departamento and ps.estadosemaforo = v_estado and pt.realizado = v_realizado;




end;


create or replace procedure sp_listar_usuarios_departamento(
    v_id_departamento number,
    usuarios out SYS_REFCURSOR
)
is

begin

    open usuarios for select pu.id, pu.username, pu.email, ag.id, ag.name from process_user pu
                    full join process_user_groups pg on pg.user_id = pu.id
                    full join auth_group ag on ag.id = pg.group_id
                    where pu.departamento_id = v_id_departamento;


end;



create or replace procedure sp_listar_grupos(
    grupos out SYS_REFCURSOR
)
is

begin

    open grupos for select ag.id, ag.name, count(pg.id) from auth_group ag
                        full join process_user_groups pg on pg.group_id = ag.id
                        group by ag.id, ag.name;

end;

create or replace procedure sp_listar_tareas_grupo(
    v_grupo_id number,
    grupos out SYS_REFCURSOR
)
is

begin

    open grupos for select pt.id, pt.nombre, pt.realizado, pu.id, pu.username, ps.estadosemaforo from process_tarea pt
                                join process_user pu on pu.id = pt.usuario_id
                                join process_user_groups ug on ug.user_id = pu.id
                                join process_calculoestado pc on pc.id = pt.id
                                join process_semaforo ps on ps.calculoestado_id = pc.id
                                where ug.group_id = v_grupo_id
                                order by pt.realizado;

end;


create or replace procedure sp_listar_usuarios_grupo(
    v_id_grupo number,
    usuarios out SYS_REFCURSOR
)
is

begin

    open usuarios for select pu.id, pu.username, pu.email, ag.id, ag.name from process_user pu
                    full join process_user_groups pg on pg.user_id = pu.id
                    full join auth_group ag on ag.id = pg.group_id
                    where pg.group_id = v_id_grupo;


end;

create or replace procedure sp_listar_estado_tareas_grupo(
    v_id_grupo number,
    v_realizado number,
    v_estado varchar,
    tareas out SYS_REFCURSOR
)
is

begin

    open tareas for select pt.id, pt.nombre, pt.descripcion, pt.realizado, pt.fechacreacion, pt.fechalimite, pt.fechatermino, pt.usuario_id from process_tarea pt
                        join process_user pu on pu.id=pt.usuario_id
                        join process_user_groups ug on ug.user_id = pu.id
                        join process_calculoestado pc on pc.id = pt.id
                        join process_semaforo ps on ps.calculoestado_id = pc.id
                        where ug.group_id = v_id_grupo and ps.estadosemaforo = v_estado and pt.realizado = v_realizado;


end;

create or replace procedure sp_listar_tareas_grupo(
    v_usuario_id number,
    grupos out SYS_REFCURSOR
)
is

begin

    open grupos for select pt.id, pt.nombre, pt.realizado, pu.id, pu.username, pu.email, ps.estadosemaforo, pt.fechatermino from process_tarea pt
                    join process_user pu on pt.usuario_id = pu.id
                    join process_calculoestado pc on pc.id = pt.id
                    join process_semaforo ps on ps.calculoestado_id = pc.id
                    where pu.id = v_usuario_id
                    order by pt.realizado ;

end;
