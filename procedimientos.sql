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

    open tareas for select pt.id, pt.nombre, pt.descripcion, pt.realizado, pt.fechacreacion, pt.fechalimite, pt.fechatermino, pt.usuario_id from process_tarea pt
                        join process_user pu on pu.id=pt.usuario_id
                        where pu.departamento_id = v_id_departamento;




end;

