create schema if not exists tt;
create or replace function tt.h(p_uid text, p_sql text) returns text language plpgsql as $f$
declare r text;
begin
  perform set_config('request.jwt.claim.sub', p_uid, true);
  execute 'set local role authenticated';
  begin execute p_sql into r; exception when others then r := 'ERR: ' || sqlerrm; end;
  execute 'reset role';
  return md5(coalesce(r,'null')) || case when r like 'ERR:%' then ' ' || left(r, 40) else '' end;
end $f$;
